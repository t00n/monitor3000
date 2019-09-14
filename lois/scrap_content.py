import requests
import json
import os
from time import sleep

from tqdm import tqdm

with open('index.json') as f:
    index = json.load(f)

for dt, docs in tqdm(index.items()):
    dirname = os.path.join("raw", "content", dt)
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    for doc in tqdm(docs):
        filename = os.path.join(dirname, "{}.html".format(doc['numac']))
        if not os.path.exists(filename):
            while True:
                try:
                    response = requests.get(doc['url'])
                    break
                except:
                    sleep(60)
            if response.ok:
                with open(filename, 'wb') as f:
                    f.write(response.content)
            sleep(0.5)
