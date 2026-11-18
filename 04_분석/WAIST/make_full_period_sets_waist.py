#!/usr/bin/env python3
#  입력: 주 풀(EXT_canonical_pool_WAIST.csv) + 02_패널/WAISTF_Estd3w.csv 2018 분자·분모 → EXT_canonical_pool_WAIST_full.csv, sets_WAIST_full.json
import os, json, unicodedata
import pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); PAN = os.path.join(os.path.dirname(os.path.dirname(HERE)), "02_패널")
P = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_WAIST.csv")); P["fbd_region"] = P.fbd_region.map(NFC)
F = pd.read_csv(os.path.join(PAN, "WAISTF_Estd3w.csv")); F["fbd_region"] = F.fbd_region.map(NFC); f18 = F[F.year == 2018].set_index("fbd_region")
m = P.year == 2018; P.loc[m, "waist_cases"] = P.loc[m, "fbd_region"].map(f18.cases).values; P.loc[m, "waist_examinees"] = P.loc[m, "fbd_region"].map(f18.offset).values
assert P[P.year.between(2013, 2024)][["waist_cases", "waist_examinees"]].notna().all().all()
P.to_csv(os.path.join(PAN, "EXT_canonical_pool_WAIST_full.csv"), index=False, encoding="utf-8-sig")
j = json.load(open(os.path.join(HERE, "sets_WAIST_main.json"), encoding="utf-8"))
j["offset_E_file"] = "WAISTF_Estd3w.csv"; j["rules"]["years"] = [2013, 2024]; j["rules"]["windows"] = {"W1_2013-18": [2013, 2018], "W2_2019-24": [2019, 2024]}; j["rules"]["covid_post_from"] = 2020
j["extra_columns"] = {k: ["EXT_canonical_pool_WAIST_full.csv", v[1]] for k, v in j["extra_columns"].items()}
j["sens_note"] = "2013-2024 including 2018"; j["offset_E_label"] = j["offset_E_label"].replace("2019-2024", "2013-2024")
json.dump(j, open(os.path.join(HERE, "sets_WAIST_full.json"), "w"), ensure_ascii=False, indent=1)
