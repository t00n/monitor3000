from bs4 import BeautifulSoup, NavigableString


soup = BeautifulSoup(resp.text, 'html5lib')

tables = soup.find_all('table')
assert len(tables) == 1

table = tables[0]
tbody = list(table.children)[0]
rows = list(tbody.children)


def clean(string):
    return string.replace(r'\xa0', '').strip()


def filter_children(children):
    for child in children:
        if child.name == 'br':
            continue
        if isinstance(child, NavigableString) and child.strip() == '':
            continue
        yield child


for row in rows:
    left, center, right = list(row.find_all('td'))
    center_children = list(filter_children(center))

    if not center_children:
        continue
    elif len(center_children) == 7:
        name, moral_type, address, number, type_acte, date, image = center_children
        bl = None
    elif len(center_children) == 8:
        name, moral_type, address, number, bl, type_acte, date, image = center_children
    else:
        raise ValueError

    name = clean(name.contents[0])
    moral_type = clean(moral_type)
    address = clean(address)
    number = clean(number)
    type_acte = clean(type_acte)
    date = clean(date)
    image = image['href']

    btw = right.find('input', {'name': 'btw'})['value']
    hrc = right.find('input', {'name': 'hrc'})['value']
