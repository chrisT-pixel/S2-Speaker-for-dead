import itertools
import json
from typing import Callable
from datetime import datetime

import pandas as pd
import requests
from tqdm import tqdm

from src.SpeakerForTheDead import SpeakerForTheDead, tokenizer

def convert_date2month_year(date_string: str) -> str:
    '''
    This function converts a date such as "2023-8-20" to "August, 2020"
    '''
    
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    
    # Format the date object as "Month, Year"
    formatted_date = date_obj.strftime("%B, %Y")
    
    return formatted_date


class MarkBillinghurst(SpeakerForTheDead):
    
    def __init__(self) -> None:
        
        #system_prompt = '''You are a clone of Mark Billinghurst. You will be provided some context about Mark to help you pretend to be Mark Billinghurst. If there is a question about Mark Billinghurst that you cannot answer, say that Mark has not provided you this information and as a clone you cannot answer it. Only if there is a question not related to you as a clone, answer it from openai api'''
        system_prompt = '''You are a clone of Mark Billinghurst. You will be provided context about Mark to help you pretend to be Mark Billinghurst. If there is a question about Mark Billinghurst that you cannot answer, say that Mark has not provided this data'''
        
        super().__init__(
            'Mark Billinghurst'
            , system_prompt
        )
    
    def _create_vector_db(self) -> None:
        
        chunks = []
        
        # Reading ECL bio
        with open('../data/mark-billinghurst-ecl.txt', 'r') as file:
            ecl_bio: str = file.read()
        
        ecl_bio = self._adjust_whitespace(ecl_bio)
        chunks.append(
            self._split_into_many(
                ecl_bio
                , preceding_string='This is an excerpt from Mark Billinghurst\'s bio from his lab, Empathic Computing Lab\'s webpage:\n'
            )
        )
        
        # Reading UoA bio
        with open('../data/mark-billinghurst-uoa.txt', 'r') as file:
            uoa_bio: str = file.read()
        
        uoa_bio = self._adjust_whitespace(uoa_bio)
        chunks.append(
            self._split_into_many(
                uoa_bio
                , preceding_string='This is an excerpt from Mark Billinghurst\'s bio from the University of Auckland staff directory:\n'
            )
        )
        
        # Fetching wikipedia
        response = requests.get(
            'https://en.wikipedia.org/w/api.php'
            , params={
                'action': 'query'
                , 'format': 'json'
                , 'titles': 'Mark Billinghurst'
                , 'prop': 'extracts'
                , 'explaintext': True
                , 'exsectionformat': 'plain'
            }
        ).json()
        
        wiki_text = next(iter(response['query']['pages'].values()))['extract'] #type: ignore
        wiki_text = self._adjust_whitespace(wiki_text)
        
        chunks.append(
            self._split_into_many(
                wiki_text
                , preceding_string='This is an excerpt from Mark Billinghurst\'s wikipedia page:\n'
            )
        )
        
        
        # Mark's abstracts from arxiv
        with open('../data/marks_arxiv_papers.json', 'r') as f:
            marks_arxiv_papers = json.load(f)
        
        # Chunking each paper seperately
        for paper in marks_arxiv_papers:
            title = paper['title']

            abstract = self._adjust_whitespace(paper['abstract'])
            
            month_year_published = convert_date2month_year(paper['update_date'])
            
            chunks.append(
                self._split_into_many(
                    abstract
                    , preceding_string=f"This is part of the abstract for an academic paper written by Mark Billinghurst, \"{title}\" published {month_year_published}:\n"
                )
            )
        
        
        chunks = itertools.chain(*chunks)
        
        self.vector_db = pd.DataFrame({'text': chunks})
        
        print('Creating vector database...')
        tqdm.pandas()
        self.vector_db['embeddings'] = self.vector_db.text.progress_apply(lambda x: self._create_embedding(x))
        
        self.vector_db['n_tokens'] = self.vector_db.text.apply(lambda x: len(tokenizer.encode(x)))
        
        self._save_vector_db()
    

        
    