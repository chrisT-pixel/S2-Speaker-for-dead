import os
from typing import Callable

import pandas as pd
from tqdm import tqdm

from src.SpeakerForTheDead import SpeakerForTheDead, tokenizer

def create_new_character(clone_name):

    class CustomClone(SpeakerForTheDead):
        
        def __init__(self, clone_name) -> None:
            super().__init__(clone_name)
     
        def _create_vector_db(self) -> None:
            
            # Reading custom biography retreived from uploaded folder
            with open('clone_info_uploads/' + clone_name + '.txt', 'r', encoding='utf-8') as file:
                bio: str = file.read()
            
            bio = self._adjust_whitespace(bio)
            
            chunks = self._split_into_many(
                bio
                , preceding_string='This is an excerpt from the'  + clone_name + ' biography.'
            )
            
            
            self.vector_db = pd.DataFrame({'text': chunks})
            
            tqdm.pandas()
            self.vector_db['embeddings'] = self.vector_db.text.progress_apply(lambda x: self._create_embedding(x))
            
    
            self.vector_db['n_tokens'] = self.vector_db.text.apply(lambda x: len(tokenizer.encode(x)))
            
            # Saving vector database
            self._save_vector_db()
    
    # Create an instance of CustomClone with clone_name as an argument
    custom_clone_instance = CustomClone(clone_name)
    return custom_clone_instance

