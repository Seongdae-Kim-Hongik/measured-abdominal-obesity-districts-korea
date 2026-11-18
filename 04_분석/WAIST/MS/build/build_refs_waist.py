import json, os, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
O = json.load(open(os.path.join(AN, "OBES/MS/build/refs_obes.json"))); L = json.load(open(os.path.join(AN, "LIPS/MS/build/refs_lips.json")))
PM = {"jeong2026nationwide": 42139307, "cho2018differential": 30092838, "kim2021guidelines": 34045368, "jang2021trends": 33920007, "yoo2010general": 20955726,
      "morris2015heavier": 26264275, "quick2020trends": 31688128, "rosmond1998stress": 9626108}
FROM_O = ["kim2026obesity", "maukonen2018comparison", "dwyerlindgren2013prevalence", "area2023inequalities", "food2024environment", "walkability2019adults",
          "traversy2015alcohol", "wardle2011stress", "swinburn1999dissecting", "yoon2014community", "hodges2010adding", "web:mois2026licence"]
FROM_L = ["cheolseong2017data", "kang2015korea", "inskip1983methods", "besag1991bayesian", "riebler2016intuitive", "simpson2017penalising", "rue2009approximate",
          "gelman2014understanding", "knorrheld2000bayesian", "steegen2016increasing", "dupont2022spatial", "lipsitch2010negative", "bell2015explaining", "ord1995local",
          "morgenstern1995ecologic", "web:mois2026population", "web:rcore2026"]
R = {}
d = json.loads(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", id=",".join(str(v) for v in PM.values()), retmode="json")), timeout=60).read())["result"]
for k, p in PM.items():
    x = d[str(p)]; doi = next((a["value"] for a in x.get("articleids", []) if a["idtype"] == "doi"), "")
    au = [a["name"] for a in x.get("authors", []) if a.get("authtype") == "Author"]
    R[k] = dict(type="journal", authors=au, title=x["title"].rstrip("."), journal=x["source"], year=int(x["pubdate"][:4]), vol=x.get("volume", ""), issue=x.get("issue", ""),
                pages=x.get("pages", ""), doi=doi, pmid=str(p), verified="PubMed esummary 2026-11-18")
for k in FROM_O: R[k] = dict(O[k]); R[k].setdefault("verified", "verified earlier reference set")
for k in FROM_L: R[k] = dict(L[k]); R[k].setdefault("verified", "verified earlier reference set")
for k in ("web:mois2026population", "web:rcore2026", "web:mois2026licence"): R[k]["accessed"] = "November 18, 2026"
R["web:kosis2026metabolic"] = dict(type="web", authors="National Health Insurance Service", title="National general health screening statistics: metabolic syndrome risk factors by district and sex (DT_35007_N138) and by sex and age (DT_35007_N139), general screening attendees by sex and age (DT_35007_N099), and first-stage screening targets and attendees (DT_35007_N001), 2013-2024. Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="November 18, 2026")
for k, r in R.items():
    if r.get("type") == "journal": assert r.get("doi") or r.get("pmid"), k
json.dump(R, open(os.path.join(HERE, "refs_waist.json"), "w"), ensure_ascii=False, indent=1)
for k, r in R.items(): print(k, "|", r.get("journal"), r.get("year"), r.get("vol"), r.get("pages"), r.get("doi"), "|", (r["authors"][:2] if isinstance(r["authors"], list) else r["authors"]), "|", r.get("title","")[:70])
print(len(R))
