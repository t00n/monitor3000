import requests
import json
import os

from tqdm import tqdm

with open('index.json') as f:
    index = json.load(f)

for dt, docs in tqdm(index.items()):
    for doc in tqdm(docs):
        filename = 'html/{}.html'.format(doc['numac'])
        if not os.path.exists(filename):
            response = requests.get(doc['url'])
            if response.ok:
                with open(filename, 'wb') as f:
                    f.write(response.content)
