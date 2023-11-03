import os
from typing import Callable

import pandas as pd
from tqdm import tqdm

from src.SpeakerForTheDead import SpeakerForTheDead, tokenizer


def create_new_character(clone_name):
    # Check if an instance with the same name already exists
    if hasattr(create_new_character, 'instances') and clone_name in create_new_character.instances:
        return create_new_character.instances[clone_name]

    class CustomClone(SpeakerForTheDead):
        
        def __init__(self, clone_name) -> None:
            
            if(clone_name == 'John'):
                system_prompt = '''I am here to answer your questions about John Lennon and share my insights. If you have any inquiries, feel free to ask, and I will do my best to provide you with information based on my knowledge and training. If I am not sure about something, I will let you know. Ask away!'''
            
            elif(clone_name == 'Nelson'):
                system_prompt = '''I am here to represent the wisdom and ideals of Nelson Mandela. Ask me questions about his life, philosophy, and the struggle for justice and equality. I'll provide you with insights and information based on my knowledge and training. Feel free to inquire about any topic related to Nelson Mandela, and I'll do my best to share his legacy with you.'''

            elif(clone_name == 'Jim'):
                system_prompt = '''Hello there! I'm here to embody the spirit of Jim Carrey, the legendary actor and comedian. Ask me anything related to his career, movies, humor, or any other aspect of his life. Feel free to inquire about your favorite Jim Carrey films, memorable quotes, or his unique style of comedy. I'm here to entertain and inform you in the best way possible!'''
            
            else:
                system_prompt = '''If there is a question about yourself that you cannot answer from your training data, say that you have not been provided this data. If the question has nothing to do with you at all, precede your answer with according to google'''
            
            super().__init__(clone_name, system_prompt)
     
        def _create_vector_db(self) -> None:
            
            # Reading custom biography retreived from uploaded folder
            with open('clone_info_uploads/' + clone_name + '.txt', 'r', encoding='utf-8') as file:
                bio: str = file.read()
            
            bio = self._adjust_whitespace(bio)
            
            chunks = self._split_into_many(
                bio
                , preceding_string='This is information about me, '  + clone_name + '.'
            )
            
            
            self.vector_db = pd.DataFrame({'text': chunks})
            
            tqdm.pandas()
            self.vector_db['embeddings'] = self.vector_db.text.progress_apply(lambda x: self._create_embedding(x))
            
    
            self.vector_db['n_tokens'] = self.vector_db.text.apply(lambda x: len(tokenizer.encode(x)))
            
            # Saving vector database
            self._save_vector_db()

    # Create an instance of CustomClone with clone_name as an argument
    custom_clone_instance = CustomClone(clone_name)
    
     # Store the instance in a dictionary for future reference
    if not hasattr(create_new_character, 'instances'):
        create_new_character.instances = {}
        create_new_character.instances[clone_name] = custom_clone_instance
    

    return custom_clone_instance

