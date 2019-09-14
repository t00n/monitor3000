import re
import os

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


DATE_REGEX = r'(\d{1,2}).*(' + '|'.join(MONTHS.keys()) + r').*(\d{4})'


def parse_date(header):
    header_upper = unidecode.unidecode(header).upper()
    match = re.search(DATE_REGEX, header_upper)
    day, month, year = match.groups()
    day = int(day)
    month = MONTHS[month.upper()]
    year = int(year)
    return "%04d-%02d-%02d" % (year, month, day)

TITLE_REGEX = r'(' + '|'.join(DOCUMENT_TYPES) + r')'


def parse_title(header):
    header_upper = unidecode.unidecode(header).upper()
    match = re.search(TITLE_REGEX, header_upper)
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
    prelude = None

    for splitter in ['Article 1er.', 'Article 1.', 'Art. 1.', 'Convienne', 'Article unique', 'Article Unique']:
        try:
            prelude, _ = text.split(splitter)
            break
        except:
            pass

    authorities = []
    references = []
    if prelude is not None:
        splitted = prelude.split('\n')
        i = 0
        for line in splitted:
            if line.startswith('Vu') or line.startswith('Considérant'):
                break
            authorities.append(line[:-1])
            i += 1
        references = [x[:-1] for x in splitted[i:-2]]
    return authorities, references


def parse_articles(text):
    articles = []
    i = -1
    for line in text.split('\n'):
        line = line.strip()
        first_article = False
        for start in ['Article 1er.', 'Article 1.', 'Art. 1.', 'Article unique', 'Article Unique']:
            if line.startswith(start):
                articles.append(line[len(start) + 1:] + '\n')
                first_article = True

        if not first_article:
            match = re.match(r'Art.[\s\n]+\d+.', line)
            if match:
                articles.append(line[len(match.group(0)) + 1:] + '\n')
                i += 1
            elif i >= 0:
                articles[i] += line + '\n'
    return articles


class Document:
    @staticmethod
    def from_html(html):
        doc = Document()
        doc._html = html
        doc.parse_html()
        return doc

    def parse_html(self):
        soup = BeautifulSoup(self._html, 'html.parser')
        # header
        header = soup.select('h3 > center > u')[0].text
        self.date = parse_date(header)
        self.title = parse_title(header)

        # content
        self.content = parse_content(soup)
        self.authorities, self.references = parse_prelude(self.content)
        self.articles = parse_articles(self.content)

    def __str__(self):
        return "<Document date={} title={}>".format(self.date, self.title)


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        filename = sys.argv[1]

        with open(filename, 'rb') as f:
            doc = Document.from_html(f.read())

            print(doc.date, doc.title)
            print(doc.authorities)
            print(doc.references)
            print(doc.articles)

    else:
        for dt in os.listdir("raw/content"):
            dirname = os.path.join("raw", "content", dt)

            for filename in os.listdir(dirname):
                filename = os.path.join(dirname, filename)

                # print(filename)

                with open(filename, 'rb') as f:
                    doc = Document.from_html(f.read())

                # print(doc)
                # print(doc.authorities)
                # print(doc.references)

                if not doc.authorities or not doc.references or not doc.articles:
                    print("### AUTHORITIES ###")
                    print(doc.authorities)
                    print("### REFERENCES ###")
                    print(doc.references)
                    print("### ARTICLES ###")
                    print(doc.articles)
                    print("### CONTENT ###")
                    print(doc.content)

                # print("DATE", doc.date)
                # print("TITLE", doc.title)
                # print("CONTENT", doc.content)
                # print("AUTHORITY", doc.authorities)
                # print("REFS", doc.references)
                # print("ARTICLES", doc.articles)
