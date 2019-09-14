import os
import json
from collections import defaultdict

from bs4 import BeautifulSoup
from tqdm import tqdm

index = defaultdict(lambda: [])

for dirname in tqdm(os.listdir("raw/index")):
    for filename in tqdm(os.listdir(os.path.join("raw", "index", dirname))):
        content = open(os.path.join("raw", "index", dirname, filename), "rb").read()
        soup = BeautifulSoup(content, 'html.parser')
        # iter on entries
        for form in soup.select('form[action=article\.pl]'):
            row = {}
            # lots of data are contained in a form, ready to be sent to redirect to the article page
            for input in form.select('input'):
                row[input.attrs['name']] = input.attrs['value']
            url = 'http://www.ejustice.just.fgov.be/cgi/article_body.pl?numac={}&caller={}&pub_date={}&language={}'.format(
                row['numac'],
                row['caller'],
                row['pub_date'],
                row['language'],
            )
            row['url'] = url
            index[dirname].append(row)

with open("index.json", "w") as f:
    json.dump(index, f)
