import json
from copy import copy
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'http://www.ejustice.just.fgov.be/doc/rech_f2.htm',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

search_params = (
    ('language', 'fr'),
)

search_data = [
    ('rech', 'Recherche'),
    ('trier', 'promulgation'),
    ('ddda', '1800'),
    ('dddm', '01'),
    ('dddj', '01'),
    ('ddfa', '2020'),
    ('ddfm', '01'),
    ('ddfj', '01'),
    ('pdda', '1800'),
    ('pddm', '01'),
    ('pddj', '01'),
    ('pdfa', '2020'),
    ('pdfm', '01'),
    ('pdfj', '01'),
    ('numac', ''),
    ('bron', ''),
    ('htit', ''),
    ('text1', ''),
    ('choix1', 'ET'),
    ('text2', ''),
    ('choix2', 'ET'),
    ('text3', ''),
    ('exp', ''),
    ('fr', 'f'),
    ('nl', 'n'),
    ('du', 'd'),
]

list_params = [
    ('language', 'fr'),
    ('fromtab', ' moftxt UNION montxt UNION modtxt'),
    ('trier', 'promulgation'),
    ('tri', 'dd AS RANK '),
    ('ddda', '1800'),
    ('dddm', '01'),
    ('dddj', '01'),
    ('ddfa', '2020'),
    ('ddfm', '01'),
    ('ddfj', '01'),
    ('pdda', '1800'),
    ('pddm', '01'),
    ('pddj', '01'),
    ('pdfa', '2020'),
    ('pdfm', '01'),
    ('pdfj', '01'),
    ('numac', ''),
    ('bron', ''),
    ('htit', ''),
    ('text1', ''),
    ('choix1', 'ET'),
    ('text2', ''),
    ('choix2', 'ET'),
    ('text3', ''),
    ('exp', ''),
    ('', ''),
    ('fr', 'f'),
    ('nl', 'n'),
    ('du', 'd'),
    ('an', ''),
]

DOCUMENT_TYPES = [
    "ACCORD DE COOPERATION",
    "ACCORD NATIONAL",
    "ARRETE",
    "ARRETE ROYAL",
    "ARRETE MINISTERIEL",
    "AVIS",
    "CIRCULAIRE",
    "DECRET",
    "LOI",
    "LOI-PROGRAMME",
    "LOI DE FINANCES",
    "ORDONNANCE",
    "REGLEMENT",
    "UNIONS PROFESSIONNELLES",
]

index = defaultdict(lambda: [])

for dt in tqdm(DOCUMENT_TYPES):
    # get n_results
    data = copy(search_data)
    data.append(('dt', dt))
    response = requests.post('http://www.ejustice.just.fgov.be/cgi/rech.pl', headers=headers, params=search_params, data=data)
    soup = BeautifulSoup(response.content, 'html.parser')
    n_results = int(list(list(soup.select('table')[0].children)[1].children)[1].text)

    # iter result pages
    for i in tqdm(range(1, n_results + 1, 100)):
        params = copy(list_params)
        params.append(
            ('sql', 'dt = \'{}\' and dd between date\'1800-01-01\' and date\'2020-01-01\'  and pd between date\'1800-01-01\' and date\'2020-01-01\' '.format(dt))
        )
        params.append(
            ('rech', '{}'.format(n_results))
        )
        params.append(
            ('dt', '{}'.format(dt))
        )
        params.append(
            ('row_id', i)
        )
        response = requests.get('http://www.ejustice.just.fgov.be/cgi/list_body.pl', headers=headers, params=params)
        soup = BeautifulSoup(response.content, 'html.parser')
        # iter on entries
        for form in soup.select('form[action=article.pl]'):
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
            index[dt].append(row)

with open("index.json", "w") as f:
    json.dump(index, f)
