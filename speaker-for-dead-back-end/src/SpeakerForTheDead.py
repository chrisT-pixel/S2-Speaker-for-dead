import os
import time
from typing import Callable, List, Tuple, Union

import re #for new converse_with_chunks function
from typing import Generator #for new converse_with_chunks function

import numpy as np
import openai
import pandas as pd
import tiktoken
from openai.embeddings_utils import distances_from_embeddings
from tenacity import retry, stop_after_attempt, wait_random_exponential

from src.api_key import open_ai_key

openai.api_key = open_ai_key
tokenizer = tiktoken.get_encoding("cl100k_base")

class SpeakerForTheDead:
    '''
    Base class for all characters. This class contains methods that all
    characters will share.
    
    To create new characters, inherit this class and:
    - override `__init__` to define system prompt and name
    - override `_create_vector_db` to define a vector database (not required).
    '''
    
    def __init__(self, name: str = 'GPT', system_prompt = '') -> None:
        self.name: str = name
        
        self.vector_db: pd.DataFrame = pd.DataFrame({})
        self.vector_db_path: str = os.path.join('../saved_vector_db', self.name, 'embeddings.parquet.gzip')
        
        self._load_vector_db()
        
        
        self.system_prompt: str = system_prompt
    
        self.convo_history: List[str] = []
        self.convo_history_tokens: List[int] = []
        self.current_tokens: int = len(tokenizer.encode(system_prompt))
        
        self.llm_input_limit = 4096
        
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10))
    def _create_embedding(self, x: str, engine: str='text-embedding-ada-002', sleep: float=1) -> np.ndarray:
        
        embedding = np.array(openai.Embedding.create(input=x, engine='text-embedding-ada-002')['data'][0]['embedding']) #type: ignore
    
        time.sleep(sleep)
        return embedding

    def _save_vector_db(self) -> None:
        # Checks if directory exists, otherwise creates it.        
        if not os.path.exists(os.path.join('../saved_vector_db',self.name)):
            os.mkdir(os.path.join('../saved_vector_db',self.name))
    
        self.vector_db.to_parquet(self.vector_db_path, compression='gzip')
            
    def _load_vector_db(self) -> None:
        if os.path.exists(self.vector_db_path):
            self.vector_db = pd.read_parquet(self.vector_db_path)
            
        else:
            self._create_vector_db()
    
    def _create_vector_db(self) -> None:
        pass
    
    def _create_context(self, question: str, max_len: int = 1800) -> str:
        
        if not self.vector_db.empty:
        
            # Get the embeddings for the question
            q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding'] # type: ignore
            
            self.vector_db['distances'] = distances_from_embeddings(q_embeddings, self.vector_db['embeddings'].values, distance_metric='L1') # type: ignore
            
            returns: List[str] = []
            current_len: int = 0
            
            # Sort by distance and add the text to the context until the context is too long
            for _, row in self.vector_db.sort_values('distances', ascending=True).iterrows():
                
                # Add the length of the text to the current length
                current_len += row['n_tokens'] + 4
                
                # If the context is too long, break
                if current_len > max_len:
                    break
                
                # Else add it to the text that is being returned
                returns.append(row["text"])
            
            # Return the context
            return "\n\n###\n\n".join(returns)
        
        else:
            return ''
    
    @staticmethod
    def _adjust_whitespace(x: str) -> str:
        x = x.replace('\n', ' ')
        x = x.replace('\\n', ' ')
        x = x.replace('  ', ' ')
        x = x.replace('  ', ' ')
        
        return x
    
    @staticmethod
    def _split_into_many(
        text
        , max_tokens = 500
        , preceding_string = 'This is an excerpt from the Mark Twain biography:\n'
    ):

        # Split the text into sentences
        sentences = text.split('. ')

        # Get the number of tokens for each sentence
        n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]
        total_tokens = sum(n_tokens)
        
        preceding_string_tokens = len(tokenizer.encode(preceding_string))
        
        if sum(n_tokens) < 0:
            return []
        
        chunks = []
        tokens_so_far = 0
        chunk = []
        
        # chunks_filled = False

        tokens_looped_through = 0
        # Loop through the sentences and tokens joined together in a tuple
        for sentence, token in zip(sentences, n_tokens):
            tokens_looped_through += token

            # If the number of tokens so far plus the number of tokens in the current sentence is greater 
            # than the max number of tokens, then add the chunk to the list of chunks and reset
            # the chunk and tokens so far
            if (tokens_so_far + token + preceding_string_tokens > max_tokens):
                chunks.append(preceding_string + ". ".join(chunk) + ".")
                chunk = []
                tokens_so_far = 0
                
                chunks_filled = True

            # If the number of tokens in the current sentence is greater than the max number of 
            # tokens, go to the next sentence
            if token + preceding_string_tokens > max_tokens:
                continue

            # Otherwise, add the sentence to the chunk and add the number of tokens to the total
            chunk.append(sentence)
            tokens_so_far += token + 1

        # if not chunks_filled:
        chunks.append(preceding_string + ". ".join(chunk) + ".")
        
        return chunks
    
    def converse(self, input_message: str, response_max_tokens: int = 500, debug_context: bool = False, time_it: bool = False) -> Union[str, Tuple[str, str]]:
        '''
        This function returns a response for an input message.
        All previous input messages are stored internally to remember conversation history.
        If conversation goes over the context length, oldest conversations are deleted to
        make room.
        
        Use method `SpeakerForTheDead.reset_conversation_history()` to reset history.
        
        Paramters:
        ----------
        - input_message: `str` - Your question to the character. History not needed, it is automatically collected.
        - response_max_tokens: `int` - The `max_tokens` parameters in `openai.Completion.create()`.
        - debug_context (optional): `bool` - Returns the context supplied for the question as well.
        - time_it (optional): `bool` - Prints out time taken to create context and response of OpenAI API.
        
        Returns:
        --------
        - output_message: `str` - Response by the character.
        - context: `str` - Only returned if `debug_context = True`
        
        Notes:
        ------
        - When forming contexts and prompts, a 10 token buffer is used.
        '''
        buffer_tokens = 100
        
        input_message = f'User: {input_message}'
        input_message_tokens: int = len(tokenizer.encode(input_message))

            
        self.convo_history.append(input_message)
        self.convo_history_tokens.append(input_message_tokens)
        self.current_tokens += input_message_tokens
        
        
        if self.current_tokens + response_max_tokens + buffer_tokens >= self.llm_input_limit:
            
            takeout_sum: int = 0
            
            for i in range(len(self.convo_history)):
                
                takeout_sum += self.convo_history_tokens[i]
                
                if self.llm_input_limit - takeout_sum - buffer_tokens > response_max_tokens:
                    self.convo_history = self.convo_history[i+1:]
                    self.convo_history_tokens = self.convo_history_tokens[i+1:]
                    self.current_tokens -= takeout_sum
                    
                    break
                    
                
        current_convo: str = "\n".join(self.convo_history)
        
        if not time_it:
            context: str = self._create_context(current_convo, max_len=self.llm_input_limit - self.current_tokens - response_max_tokens - buffer_tokens)
        
            response: dict = openai.Completion.create( # type: ignore
                prompt = f"""{self.system_prompt}
                Context: {context}
                {current_convo}
                {self.name}: """
                , temperature=0
                , max_tokens=response_max_tokens
                , top_p=1
                , frequency_penalty=0
                , presence_penalty=0
                , stop=None
                , model='text-davinci-003'
            )
            
        else:
            start_vector_search = time.time()
            context: str = self._create_context(current_convo, max_len=self.llm_input_limit - self.current_tokens - response_max_tokens - buffer_tokens)
            end_vector_search = time.time()
            
            start_openai_query = time.time()
            response: dict = openai.Completion.create( # type: ignore
                prompt = f"""{self.system_prompt}
                Context: {context}
                {current_convo}
                {self.name}: """
                , temperature=0
                , max_tokens=response_max_tokens
                , top_p=1
                , frequency_penalty=0
                , presence_penalty=0
                , stop=None
                , model='text-davinci-003'
            )
            end_openai_query = time.time()
            
            print(f'Vector search time: {end_vector_search - start_vector_search}')
            print(f'OpenAI query time: {end_openai_query - start_openai_query}')
            
            
        
        
        output_message = f'{response["choices"][0]["text"].strip()}'
        
        self.convo_history.append(output_message)
        output_message_tokens = len(tokenizer.encode(output_message))
        self.convo_history_tokens.append(output_message_tokens)
        self.current_tokens += output_message_tokens
        
        if not debug_context:
            return output_message
        else:
            return output_message, context
        
    def conversation_loop(
        self
        , turns: int = -1
        , console_disp_func: Callable = print
    ) -> None:
        '''
        Creates a conversation loop. You do not have to manually feed the
        output again and again each time.
        
        This is probably just for playing around with.
        
        Use turns = -1 for infinte loop.
        '''
        
        turns = 9999 if turns == -1 else turns
        
        turn = 0
        while True:
        
            input_message = input('Type "quit" at anytime to exit')
            console_disp_func(f'User: {input_message}')
            
            if input_message.upper() != 'QUIT':
                
                output = self.converse(input_message)
                
                console_disp_func(f'{self.name}: {output}')
                
            else:
                break
            
            if turn > turns:
                break
                
    def reset_conversation_history(self) -> None:
        '''
        Rests conversation history.
        
        After this, when you call `conversation_loop`, it will have no conversation memory.
        '''
        self.convo_history = []
        self.convo_history_tokens = []
        self.current_tokens = len(tokenizer.encode(self.system_prompt))
        
    
    
    def converse_with_word_chunks_generator(self, input_message: str, response_max_tokens: int = 500, chunk_size_words: int = 10, debug_context: bool = False, time_it: bool = False) -> Generator[str, None, None]:
        buffer_tokens = 100
    
        input_message = f'User: {input_message}'
        input_message_tokens: int = len(tokenizer.encode(input_message))
    
        self.convo_history.append(input_message)
        self.convo_history_tokens.append(input_message_tokens)
        self.current_tokens += input_message_tokens
    
        if self.current_tokens + response_max_tokens + buffer_tokens >= self.llm_input_limit:
    
            takeout_sum: int = 0
    
            for i in range(len(self.convo_history)):
    
                takeout_sum += self.convo_history_tokens[i]
    
                if self.llm_input_limit - takeout_sum - buffer_tokens > response_max_tokens:
                    self.convo_history = self.convo_history[i+1:]
                    self.convo_history_tokens = self.convo_history_tokens[i+1:]
                    self.current_tokens -= takeout_sum
    
                    break
    
        current_convo: str = "\n".join(self.convo_history)
    
        if not time_it:
            context: str = self._create_context(current_convo, max_len=self.llm_input_limit - self.current_tokens - response_max_tokens - buffer_tokens)
    
            response: dict = openai.Completion.create(
                prompt=f"""{self.system_prompt}
                Context: {context}
                {current_convo}
                {self.name}: """
                , temperature=0
                , max_tokens=response_max_tokens
                , top_p=1
                , frequency_penalty=0
                , presence_penalty=0
                , stop=None
                , model='text-davinci-003'
            )
        else:
            pass
    
        response_text = response["choices"][0]["text"].strip()
        #output_message = f'{response["choices"][0]["text"].strip()}'
        words = re.findall(r'\w+', response_text)
        output_chunks = []
    
        chunk = []
        current_chunk_words = 0
    
        for word in words:
            word_tokens = len(tokenizer.encode(word))
            if current_chunk_words + word_tokens + 1 <= chunk_size_words:
                chunk.append(word)
                current_chunk_words += word_tokens + 1  # Account for the space after each word
            else:
                output_chunk = ' '.join(chunk) + ' '
                output_chunks.append(output_chunk)
                chunk = [word]
                current_chunk_words = word_tokens + 1
    
        if chunk:
            output_chunk = ' '.join(chunk) + ' '
            output_chunks.append(output_chunk)
    
        for output_chunk in output_chunks:
            yield output_chunk
    
        self.convo_history.append(response_text)
        response_tokens = len(tokenizer.encode(response_text))
        self.convo_history_tokens.append(response_tokens)
        self.current_tokens += response_tokens
        
        #return output_message
        
        

    





        
    
    
        

        
        