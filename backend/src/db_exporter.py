from pprint import pprint
from matplotlib import pyplot as plt
from collections import Counter
from functools import cache, reduce
from os.path import join

from backend.src import db
from statistics import mean, stdev


def prepare_csv(l, sep=','):
    def quote_cell(s):
        return '"'+str(s.replace('"', '""'))+'"'
    return sep.join([quote_cell(s) for s in l]) + "\n"

def export_to_csv(dest, filtr={}):
    with open(dest, "w", encoding="utf-8") as f:
        colname = "IDFMI,LANG,Libelle,URL".split()
        for e in db.db.wikimesh.find({**filtr, **{"langs": {'$ne': None}}}):
            for lang, traduction in e["langs"].items():
                f.write(prepare_csv([
                    e["_id"].replace('EFMI_', ''),
                    # e["title"],
                    lang,
                    traduction,
                    f"https://{lang}.wikipedia.org/wiki/{traduction}"
                ]))


def safe_mean(l):
    return 0 if len(l)==0 else mean(l)

def safe_stdev(l):
    return 0 if len(l)<2 else stdev(l)

def safe_min(l):
    return 0 if len(l) == 0 else min(l)

def safe_max(l):
    return 0 if len(l) == 0 else max(l)


def describe(l):
    d = {
        "n": len(l),
        "mean": safe_mean(l),
        "sd": safe_stdev(l),
        "min": safe_min(l),
        "max": safe_max(l),
        "zero": len([e for e in l if e==0])
    }
    d['zero_frac'] = d["zero"] / d["n"] if len(l)>0 else 0
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

def normalize(s):
    return (s or "").lower().strip()

def find(l, predicate, extract=lambda e: e):
    for e in l:
        if predicate(e):
            return extract(e)

def setPath(d, path, f):
    # print(d, path)
    if type(path) == str:
        path=path.split('/')
    [p, *ps] = path
    if len(ps) == 0:
        d[p] = f(d.get(p))
    else:
        if p not in d:
            d[p] = {}
        setPath(d[p], ps, f)
    return d

def sumdicts(da, db):
    d = {}
    for k in set(list(da.keys()) + list(db.keys())):
        d[k] = da.get(k, 0) + db.get(k, 0)
    return d


@cache
def list_match_mesh_wiki(identifier):
    print(f"**** list_match_mesh_wiki called for {repr(identifier)} ****")
    def get_wikilangs(m):
        return m['wikilangs'].get("langs", {}) or {}
    
    def f(m):
        def find_lang_match(lang):
            wikilang = normalize(get_wikilangs(m).get(lang))
            meshlang = find(m['langs'], lambda e: e['_id']==lang)
            if meshlang is None:
                return "not_in_mesh"
            elif wikilang is None or not len(wikilang):
                # raise Exception(f"not in wiki: [{lang}] -->\n{m}")
                return "not_in_wiki"
            else:
                if normalize(meshlang['pt']) == wikilang:
                    return "pt"
                else:
                    if any([normalize(e) == wikilang for e in meshlang.get('syns', [])]):
                        return "syn"
                    else:
                        return "no_match"
                
        alllangs = list(set([ee for e in [
            list(get_wikilangs(m).keys()), [e['_id'] for e in m['langs']]
        ] for ee in e]))
        
        return {lang: find_lang_match(lang) for lang in alllangs}
        
    # for m in db.db.mesh_view.find({"identifier": identifier}):
    #         yield f(m)
    return [f(m) for m in db.db.mesh_view.find({"identifier": identifier})]


def gen_report(**filtr):
    all_links = [keys_if_not_None(e["langs"]) for e in db.db.wikimesh.find(filtr, {"_id": 0, "langs": 1})]
    lens = list(map(len, all_links))
    return {
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


@cache
def report_match_mesh_wiki(identifier):
    print('**** report_match_mesh_wiki ****', identifier)
    # pprint(db.db.mesh_view.find_one())
    # # [{'cs': 'not_in_wiki', 'ja': 'not_in_wiki', 'ru': 'not_in_wiki', 'en': 'syn', 'de': 'not_in_wiki', ...}]
    l = list(list_match_mesh_wiki(identifier))
    print("len(l) -> ", len(l), " -- ", repr(identifier))
    # l[0]
    # pprint(l[:5])
    # pprint(next(l))
    def combine(acc, e):
        for lang, match in e.items():
            setPath(acc, join(lang, match), lambda ee: (ee or 0)+1)
        return acc
    
    summary = reduce(combine, l, {})
    summary['overall'] = reduce(sumdicts, summary.values())
    # summary['overall']
    return summary


@cache
def report_new_langs(identifier):
    # pprint(db.db.mesh_view.find_one())
    # # [{'cs': 'not_in_wiki', 'ja': 'not_in_wiki', 'ru': 'not_in_wiki', 'en': 'syn', 'de': 'not_in_wiki', ...}]
    l = list(list_match_mesh_wiki(identifier))
    # len(l)
    return list(Counter([len([e for e in ee.values() if e == "not_in_mesh"]) for ee in l]).items())

# @cache
# def mesh_stats():
#     def run_identifier(identifier):
#         all_links = gen_report({"identifier": identifier})
#         def prepare_contingency(e):
#             e["lang_match"] = "en" if e["lang_match"] == "en" else "not_en"
#             return e

#         l = [prepare_contingency(e) for e in db.db.wikimesh.find({"identifier": identifier,'langs': {"$ne": None}}, {"_id": 0, "origin": 1, "lang_match": 1})]
#         ka = "origin"
#         kb = "lang_match"

#         return {
#             **all_links,
#             **dict(
#                 not_en = gen_report({"identifier": identifier, "lang_match": {"$ne": "en"}, "langs": {"$ne": None}}),
#                 en =     gen_report({"identifier": identifier, "lang_match": "en"}),
#                 pt =     gen_report({"identifier": identifier, "origin": "pt"}),
#                 syn =    gen_report({"identifier": identifier, "origin": "syn"}),
#             ),
#             "contingency": [
#                 [[kae, kbe], len([e for e in l if e[ka]==kae and e[kb]==kbe])]
#                 for kae in set([e[ka] for e in l])
#                 for kbe in set([e[kb] for e in l])
#             ],
#             'match_report': report_match_mesh_wiki(identifier),
#         }
#     return {
#         id: run_identifier(id)
#         for id in db.db.mesh.distinct("identifier")
#     }


@cache
def get_all_reports(identifier):
    return dict(
                all = gen_report(identifier=identifier),
                not_en = gen_report(identifier=identifier, lang_match={"$ne": "en"}, langs={"$ne": None}),
                en =     gen_report(identifier=identifier, lang_match="en"),
                pt =     gen_report(identifier=identifier, origin="pt"),
                syn =    gen_report(identifier=identifier, origin="syn"),
            )

@cache
def mesh_stats():
    identifier = "MeSH"
    def run_identifier(identifier):
        lang_per_mesh = list(db.db.mesh_view.aggregate([{"$match": {"identifier": identifier}}, {"$project": {"langs": 1, "wikilangs.langs": {"$ifNull": ["$wikilangs.langs", {}] }}}, {"$project": {"kmlangs": {"$size": "$langs"}, "kwlangs": {"$size": {"$objectToArray": "$wikilangs.langs"}}, "_id": 0}}]))
        
        
        mesh_terms_stats = {k: describe([e[f"k{k[0]}langs"] for e in lang_per_mesh]) for k in "mesh wiki".split()}
        
        def prepare_contingency(e):
            e["lang_match"] = "en" if e["lang_match"] == "en" else "not_en"
            return e

        l = [prepare_contingency(e) for e in db.db.wikimesh.find({"identifier": identifier,'langs': {"$ne": None}}, {"_id": 0, "origin": 1, "lang_match": 1})]
        ka = "origin"
        kb = "lang_match"
        return {
            **get_all_reports(identifier),
            "origins": {
                k: v
                for k, v in Counter([
                        e.get('origin')
                        for e in db.db.mesh_view.aggregate([{"$match": {"identifier": identifier}}, {"$project": {"origin": "$wikilangs.origin"}}])
                ]).items()
                if k is not None
            },
            "contingency": [
                [[kae, kbe], len([e for e in l if e[ka]==kae and e[kb]==kbe])]
                for kae in set([e[ka] for e in l])
                for kbe in set([e[kb] for e in l])
            ],
            "new_langs": report_new_langs(identifier),
            'match_report': report_match_mesh_wiki(identifier),
            'mesh_terms_stats': mesh_terms_stats
        }
    return {
        id: run_identifier(id)
        for id in db.db.mesh.distinct("identifier")
    }



if __name__ == "__main__":
    from sys import argv
    db.connect()
    
    if argv[1] == "stats":
        mesh_report()
    else:
        if len(argv) > 2:
            filtr = {'identifier': argv[2]}
        else:
            filtr = {}
        export_to_csv(argv[1], filtr)
