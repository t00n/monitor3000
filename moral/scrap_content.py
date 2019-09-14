import datetime
import requests
from tqdm import tqdm
import os

BASE = (
    "http://www.ejustice.just.fgov.be/cgi_tsv/"
    "tsv_l_1.pl?row_id={cursor}&lang=fr&fromtab=TSV&akte={category}"
    "&sql=pd+between+date%27{start.year}-{start.month}-{start.day}%27+and+date%27{end.year}-{end.month}-{end.day}%27+"
    "+and+akte+contains+%27{category}%27"
)

START = datetime.datetime(2003, 7, 1)
END = datetime.datetime.now()

BASEDIR = "raw/index"

CATEGORIES = {
    "c01": "rubrique constitution (nouvelle personne morale, ouverture succursale, etc...)",
    "c02": "rubrique fin (cessation, annulation cessation, nullité, conc, réorganisation judiciaire, etc...)",
    "c03": "dénomination",
    "c04": "selected >siège social",
    "c05": "adresse autre que siège social",
    "c06": "objet ",
    "c07": "capital, actions",
    "c08": "démissions, nominations",
    "c09": "assemblée générale ",
    "c10": "année comptable",
    "c11": "Statuts (traduction, coordination, autres modifications, …)",
    "c12": "modification forme juridique",
    "c13": "rubrique restructuration  (fusion, scission, transfert patrimoine, etc...)",
    "c14": "comptes annuels			",
    "c15": "divers",
    "c16": "radiation d'office n° BCE",
}


if __name__ == '__main__':
    if not os.path.exists(BASEDIR):
        os.makedirs(BASEDIR)

    delta = (END - START).days
    for dt in tqdm(range(delta), desc="Days"):
        s = START + datetime.timedelta(days=dt)
        e = START + datetime.timedelta(days=dt + 1)

        for cat in tqdm(sorted(CATEGORIES.keys()), desc="Categories"):
            response = None
            cursor = 0

            while True:
                filename = os.path.join(BASEDIR, "{:%Y-%m-%d}-{}-{}".format(s, cat, cursor))
                if not os.path.exists(filename):
                    response = requests.get(BASE.format(start=s, end=e, cursor=cursor, category=cat))

                    with open(filename, "wb") as f:
                        f.write(response.content)

                if response and "Fin de la liste" in response.text:
                    break
                if cursor > 20_000:
                    print("Over 20k results, this seems strange, skipping")
                    print(s, e, cursor)
                    break

                cursor += 20
