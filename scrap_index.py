import os
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

if __name__ == '__main__':
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

            dirname = os.path.join("raw", "index", dt)
            filename = os.path.join(dirname, "%08d.html" % i)

            if not os.path.exists(filename):
                if not os.path.isdir(dirname):
                    os.mkdir(dirname)

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

                with open(filename, "wb") as f:
                    f.write(response.content)
