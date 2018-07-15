import re

from bs4 import BeautifulSoup
import unidecode

from scrap_index import DOCUMENT_TYPES


MONTHS = {
    'JANVIER': 1,
    'FEVRIER': 2,
    'MARS': 3,
    'AVRIL': 4,
    'MAI': 5,
    'JUIN': 6,
    'JUILLET': 7,
    'AOUT': 8,
    'SEPTEMBRE': 9,
    'OCTOBRE': 10,
    'NOVEMBRE': 11,
    'DECEMBRE': 12,
    'JANUARI': 1,
    'FEBRUARI': 2,
    'MAART': 3,
    'APRIL': 4,
    'MEI': 5,
    'JUNI': 6,
    'JULI': 7,
    'AUGUSTUS': 8,
    'SEPTEMBER': 9,
    'OKTOBER': 10,
    'NOVEMBER': 11,
    'DECEMBER': 12,
    'JANUAR': 1,
    'FEBRUAR': 2,
    'MARZ': 3,
    'APRIL': 4,
    'MAI': 5,
    'JUNI': 6,
    'JULI': 7,
    'AUGUST': 8,
    'SEPTEMBER': 9,
    'OKTOBER': 10,
    'NOVEMBER': 11,
    'DEZEMBER': 12,
}


def parse_date(header):
    regex = r'(\d{1,2}).*(' + '|'.join(MONTHS.keys()) + r').*(\d{4})'
    match = re.search(regex, header, re.IGNORECASE)
    day, month, year = match.groups()
    day = int(day)
    month = MONTHS[month.upper()]
    year = int(year)
    return "%04d-%02d-%02d" % (year, month, day)


def parse_title(header):
    header_upper = unidecode.unidecode(header).upper()
    regex = r'(' + '|'.join(DOCUMENT_TYPES) + r')'
    match = re.search(regex, header_upper)
    index = match.start(0)
    return header[index:]


def parse_content(soup):
    h3 = soup.select('h3')[1]

    content = ''
    node = h3.next_sibling

    while not (node.name == 'a' and node.attrs.get('name', '') == 'end'):
        if node.name == 'br':
            content += '\n'
        elif node.name is not None:
            # FIXME some tags might get ignored here. example : 2018010056.html ANNEXE
            pass
        else:
            content += node.string.replace('\n', '')
        node = node.next_sibling

    content = content.strip()
    return content


def parse_prelude(text):
    prelude, _ = text.split('Article 1er.')
    splitted = prelude.split('\n')
    authority = splitted[0][:-1]
    references = [x[:-1] for x in splitted[1:-2]]
    return authority, references


def parse_articles(text):
    articles = []
    i = -1
    for line in text.split('\n'):
        if line.startswith('Article 1er.'):
            articles.append(line[13:] + '\n')
            i += 1
        else:
            match = re.match(r'Art.[\s\n]+\d+.', line)
            if match:
                articles.append(line[len(match.group(0)) + 1:] + '\n')
                i += 1
            elif i >= 0:
                articles[i] += line + '\n'
    return articles


class Document:
    def __init__(self, html):
        self._html = html
        self.parse_html()

    def parse_html(self):
        soup = BeautifulSoup(self._html, 'html.parser')
        header = soup.select('h3 > center > u')[0].text
        self.date = parse_date(header)
        self.title = parse_title(header)

    def __str__(self):
        return "<Document date={} title={}>".format(self.date, self.title)


if __name__ == '__main__':
    with open("html/2018010056.html", 'rb') as f:
        doc = Document(f.read())

    print(doc)
