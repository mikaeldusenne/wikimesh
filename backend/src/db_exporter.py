from pprint import pprint
from matplotlib import pyplot as plt
from collections import Counter
from functools import cache

from backend.src import db
from statistics import mean, stdev


def prepare_csv(l, sep=','):
    def quote_cell(s):
        return '"'+str(s.replace('"', '""'))+'"'
    return sep.join([quote_cell(s) for s in l]) + "\n"

def export_to_csv(dest):
    with open(dest, "w", encoding="utf-8") as f:
        for e in db.db.mesh.find():
            for lang, traduction in e["links"].items():
                f.write(prepare_csv([
                    e["_id"], e["title"], lang, traduction
                ]))


def describe(l):
    d = {
        "n": len(l),
        "mean": mean(l),
        "sd": stdev(l),
        "min": min(l),
        "max": max(l),
        "zero": len([e for e in l if e==0])
    }
    d['zero_frac'] = d["zero"] / d["n"]
    return d

def mesh_report():
    all_links = [e['links'] for e in db.db.mesh.find()]

    def plot_bar_langs():
        langs = sorted(
            [e for e in Counter([ee for e in all_links for ee in e.keys()]).items()],
            key=lambda e: e[1],
            reverse=True
        )
        labels = [e[0].strip() for e in langs]
        values = [e[1] for e in langs]
        plt.clf()
        fig, ax=plt.subplots(figsize=(80, 5), dpi=150)
        ax.set_title("Nombre de traductions par langue")
        ax.bar(labels, values)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', rotation_mode='anchor')
        plt.savefig("backend/countries.png")
    plot_bar_langs()

    def plot_hist_links():
        lens = list(map(len, all_links))
        pprint(describe(lens))
        ntrads = sorted(
            [e for e in Counter([e for e in lens if e>0]).items()],
            key=lambda e: e[0],
            reverse=False
        )
        labels = [str(e[0]) for e in ntrads]
        values = [e[1] for e in ntrads]

        plt.clf()
        fig, ax=plt.subplots(figsize=(10, 7), dpi=200)
        ax.set_title("Répartition du nombre de langues par entrée")
        ax.bar(labels, values)
        ticks_indexes = range(0, len(labels), 10)
        ax.set_xticks(ticks_indexes)
        ax.set_xticklabels([labels[i] for i in ticks_indexes], rotation=45, ha='right', rotation_mode='anchor')
        ax.set_xlabel("Nombre de traductions disponibles")
        ax.set_ylabel("Nombre d'entrées")
        plt.savefig("backend/histogram_n_langs.png")
    plot_hist_links()


def keys_if_not_None(e):
    if e is not None:
        return list(e.keys())
    else:
        return []

@cache
def mesh_stats():
    all_links = [keys_if_not_None(e["langs"]) for e in db.db.wikimesh.find({}, {"_id": 0, "langs": 1})]
    len([e for e in all_links if len(e) > 0])
    
    lens = list(map(len, all_links))
    return {
        # "all_links": [list(e.keys()) for e in all_links],
        "n_trads": sorted(
            [e for e in Counter([e for e in lens if e>0]).items()],
            key=lambda e: e[0],
            reverse=False
        ),
        "langs": sorted(
            [e for e in Counter([ee for e in all_links for ee in e]).items()],
            key=lambda e: e[1],
            reverse=True
        ),
        "overall": describe(lens),
    }


if __name__ == "__main__":
    from sys import argv
    db.connect()
    
    if argv[1] == "stats":
        mesh_report()
    else:
        export_to_csv(argv[1])
