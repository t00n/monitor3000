import datetime
import requests
from tqdm import tqdm
import os

BASE = (
    "http://www.ejustice.just.fgov.be/cgi_tsv/"
    "tsv_l_1.pl?row_id={cursor}&lang=fr&fromtab=TSV"
    "&sql=pd+between+date%27{start.year}-{start.month}-{start.day}%27+and+date%27{end.year}-{end.month}-{end.day}%27+"
)

START = datetime.datetime(2003, 7, 1)
END = datetime.datetime.now()

BASEDIR = "raw/index"


if __name__ == '__main__':
    if not os.path.exists(BASEDIR):
        os.makedirs(BASEDIR)

    delta = (END - START).days
    for dt in tqdm(range(delta)):
        s = START + datetime.timedelta(days=dt)
        e = START + datetime.timedelta(days=dt + 1)

        response = None
        cursor = 0

        while True:
            filename = os.path.join(BASEDIR, "{:%Y-%m-%d}-p{}".format(s, cursor))
            if not os.path.exists(filename):
                response = requests.get(BASE.format(start=s, end=e, cursor=cursor))

                with open(filename, "wb") as f:
                    f.write(response.content)

            if (response and "Fin de la liste" in response.text) or cursor > 5200:
                break

            cursor += 20
