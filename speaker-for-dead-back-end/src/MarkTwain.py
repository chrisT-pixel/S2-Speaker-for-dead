import os
from typing import Callable

import pandas as pd
from tqdm import tqdm

from src.SpeakerForTheDead import SpeakerForTheDead, tokenizer


class MarkTwain(SpeakerForTheDead):
    
    def __init__(self) -> None:
        super().__init__('Mark Twain')
 
    def _create_vector_db(self) -> None:
        
        # Reading mark twain biography retreived from gutenberg
        with open('data/mark-twain-biography.txt', 'r', encoding='utf-8') as file:
            bio: str = file.read()
        
        bio = self._adjust_whitespace(bio)
        
        chunks = self._split_into_many(
            bio
            , preceding_string='This is an excerpt from the Mark Twain biography.'
        )
        
        
        self.vector_db = pd.DataFrame({'text': chunks})
        
        tqdm.pandas()
        self.vector_db['embeddings'] = self.vector_db.text.progress_apply(lambda x: self._create_embedding(x))
        

        self.vector_db['n_tokens'] = self.vector_db.text.apply(lambda x: len(tokenizer.encode(x)))
        
        # Saving vector database
        self._save_vector_db()
        
        
        