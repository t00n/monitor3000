import re

from bs4 import BeautifulSoup


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
}


def parse_date(header):
    d = header.split('-')[0].strip()
    day, month, year = d.split(' ')
    month = MONTHS[month]
    year = year[:4]
    return "{}-{}-{}".format(year, month, day)


def parse_title(header):
    return header.split('-')[1].strip()


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
        print(html)
        self.parse_html()

    def parse_html(self):
        soup = BeautifulSoup(self._html, 'html.parser')
        header = soup.select('h3 > center > u')[0].text
        self.date = parse_date(header)
        self.title = parse_title(header)
        content = parse_content(soup)
        self.cleansed_text = header + '\n' + content
        self.authority, self.references = parse_prelude(content)
        self.articles = parse_articles(content)

    def __str__(self):
        res = self.date
        res += ' - ' + self.title + '\n\n'
        res += self.authority + ',\n'
        res += ";\n".join(self.references)
        res += ',\n'
        res += "Arrête :\n"
        for i, art in enumerate(self.articles):
            res += "Art {}. {}\n".format(i + 1, art)
        return res


if __name__ == '__main__':
    with open("html/2018010056.html", 'rb') as f:
        doc = Document(f.read())

    print(doc)
