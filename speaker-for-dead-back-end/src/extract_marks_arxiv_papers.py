import json
from tqdm import tqdm

# extracted JSON file from zip
data_file = 'data/arxiv_dataset/archive/arxiv-metadata-oai-snapshot.json'

# Generator so it doesn't load all data at once
def get_metadata():
    with open(data_file, 'r') as f:
        for line in f:
            yield line

metadata = get_metadata()

# Only takes Mark's papers
marks_papers = []
for paper in tqdm(metadata):
    paper_dict = json.loads(paper)
    
    for author in paper_dict['authors_parsed']:
        if ('Billinghurst' in author[0]) and ('M' in author[1]):
            marks_papers.append(paper_dict)

# Saves mark's papers.
with open('data/marks_arxiv_papers.json', 'w') as f:
    json.dump(marks_papers, f)
