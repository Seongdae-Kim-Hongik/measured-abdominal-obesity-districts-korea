#!/usr/bin/env python3
#  ★결과 보기 전 결정(11/18): 같은 개념에 가까운 비만 지표는 주모형에서 뺀다.
#   - KCHS 자가보고 비만율(BMI, 수준 ρ 0.59): 주모형 제외, _st_config 자동 S1b(비만 추가)로만 민감도. 이유: 허리둘레 판정과 같은 구성(체지방)이라 넣으면 질문이 'BMI를 넘어선 복부비만'으로 바뀌고 과보정.
#   - 검진 정상B 비만 비율(같은 검진의 BMI 판정, ρ 0.56): 어디에도 넣지 않는다(같은 수검자 같은 측정에서 나온 결과 성분).
#  주 2019-2024(대사 위험요인 표 수검자 = 일반검진 수검자 전원), 보조 2013-2017(ST_VER=aux), 2018 제외(표 수검자 33%, 지질검사 대상자 부분집합) — 판정 게이트 근거.
import os, json, unicodedata, hashlib
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); PAN = os.path.join(ROOT, "02_패널"); AN = os.path.join(ROOT, "04_분석")
POOL = "EXT_canonical_pool_WAIST.csv"
D = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_LIPS_261116.csv")).drop(columns=["lips_cases", "lips_examinees"]); D["fbd_region"] = D.fbd_region.map(NFC)
Y = pd.concat([pd.read_csv(os.path.join(PAN, f"{t}_Estd3w.csv")) for t in ["WAISTA", "WAIST"]])[["year", "fbd_region", "cases", "offset"]].rename(columns={"cases": "waist_cases", "offset": "waist_examinees"}); Y["fbd_region"] = Y.fbd_region.map(NFC)
O = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_OBES_261111.csv"))[["year", "fbd_region", "restaurant_per10k", "instant_food_per10k"]]; O["fbd_region"] = O.fbd_region.map(NFC)
P = D.merge(Y, on=["year", "fbd_region"], how="left", validate="one_to_one").merge(O, on=["year", "fbd_region"], how="left", validate="one_to_one"); assert len(P) == 229 * 14
yy = P.year.isin(list(range(2013, 2018)) + list(range(2019, 2025))); assert P.loc[yy, ["waist_cases", "waist_examinees"]].notna().all().all()
print("결측 칸(분자 제외):", P.drop(columns=["waist_cases", "waist_examinees"]).isna().sum()[lambda s: s > 0].to_dict())
P.to_csv(os.path.join(PAN, POOL), index=False, encoding="utf-8-sig")
# 비교 결과 METSC
S = pd.read_csv(os.path.join(AN, "METS", "panel_METS_v2.csv"), usecols=["year", "fbd_region", "cases", "E"]); S = S[S.year.between(2019, 2024)]
os.makedirs(os.path.join(AN, "METSC"), exist_ok=True); S[["year", "fbd_region", "cases"]].to_csv(os.path.join(AN, "METSC", "panel_METSC.csv"), index=False)
S.rename(columns={"E": "E_std"})[["year", "fbd_region", "E_std"]].to_csv(os.path.join(PAN, "METSC_Estd.csv"), index=False)
print("METSC", len(S), S.year.min(), S.year.max(), S.fbd_region.nunique())

FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
NEG = ["hit_and_run_rate", "traffic_culture_index", "fires_per_10000"]
SENS = ["unmet_need_rate", "living_alone_elderly"]
CARS = "eloc__DT_1YL20731__1인당자동차등록대수＜br＞(A÷B)"; STRS = "kchs__DT_H_MENTAL_STRESS__SR"
HYP = ["walking_rate", "restaurant_per10k", "instant_food_per10k", "cars_per_capita", "high_risk_drinking", "smoking_rate", "perceived_stress",
       "tertiary_educated_share", "basic_livelihood_rate", "screening_uptake"]
OBES = "kchs__DT_H_OBE_OBE__SR"
MAST = {"cars_per_capita": CARS, "perceived_stress": STRS}
XK = lambda v: OBES if v == "obesity_rate" else MAST.get(v, "ext__" + v); X = lambda L: [XK(v) for v in L]
EXPECT = {k: v.split(' (')[0] for k, v in {"walking_rate": "-", "restaurant_per10k": "+", "instant_food_per10k": "+", "cars_per_capita": "+", "high_risk_drinking": "+", "smoking_rate": "+", "perceived_stress": "+", "tertiary_educated_share": "-", "basic_livelihood_rate": "+", "screening_uptake": "-"}.items()}
SETS = {"S1_narrative_full": X(HYP),
        "S2_core": X(["walking_rate", "restaurant_per10k", "high_risk_drinking", "tertiary_educated_share", "screening_uptake"]),
        "S3_food_mobility": X(["walking_rate", "restaurant_per10k", "instant_food_per10k", "cars_per_capita"]),
        "S4_behaviour_stress": X(["high_risk_drinking", "smoking_rate", "perceived_stress"]),
        "S5_social_detection": X(["tertiary_educated_share", "basic_livelihood_rate", "screening_uptake"])}
pov = [{"year": 2023, "fbd_region": "경상남도창원시", "population": 1009038, "source": "KOSIS DT_1YL20651E 2023 통합창원시 계(유방암 11/4 population_final_audit)"}]
allv = ["waist_cases", "waist_examinees"] + FORCED + NEG + SENS + [v for v in HYP if v not in MAST]
def make(efile, years, windows, post, elabel, note_extra):
    return {
     "tag": "WAIST", "outcome_column": "ext__waist_cases",
     "outcome_label_en": "Examinees with abdominal obesity (waist circumference >=90 cm in men, >=85 cm in women) among National General Health Screening examinees (NHIS health screening statistics, metabolic syndrome risk factor table DT_35007_N138, annual)",
     "disease_en": "Screen-measured abdominal obesity (waist circumference criterion)",
     "disease_ko": "검진 복부비만(대사증후군 위험요인, 허리둘레 남 90·여 85cm 이상)",
     "offset": "ext__waist_examinees", "exclude_years": [],
     "forced": X(FORCED), "negative_controls": X(NEG),
     "offset_E_column": "E_std", "offset_E_file": efile, "offset_E_label": elabel,
     "graph": "593-edge contact graph, ST_GRAPH=04_분석/WAIST/graph_593.graph",
     "population_override": pov, "sensitivity_only_extra": X(SENS),
     "sets": SETS, "transform": {XK(v): "none" for v in FORCED + NEG + SENS + HYP},
     "expected_direction": {XK(k): v for k, v in EXPECT.items()},
     "rules": {"likelihood": "forced-only 모형 WAIC 낮은 쪽(Poisson/NB)", "set_choice": "WAIC 최소, 4 이내면 변수 적은 세트", "credible": "95% CrI 1 제외", "vif_drop": 10, "multiverse_specs": 200,
               "years": list(years), "windows": windows, "covid_post_from": post,
     "note": "Outcome: attendees with abdominal obesity (waist circumference >=90 cm men, >=85 cm women) at the general health screening (NHIS), 229 districts; expected counts standardised for sex and 15 age groups.",
     "extra_columns": {"ext__" + v: [POOL, v] for v in allv}}
LAB = "sex-and-age-standardised expected abdominal-obesity cases, 2 sexes x 15 age bands (<=19, 20-24 to 80-84, 85+) (national screening rates DT_35007_N139; district examinee age structure approximated from resident population x national uptake, sex totals observed), {}"
w_main = {"W1_2019-21": [2019, 2021], "W2_2022-24": [2022, 2024]}
for ver in ["main", "s577", "s2", "sc"]:
    j = make("WAIST_Estd3w.csv", (2019, 2024), w_main, 2020, LAB.format("2019-2024"), "")
    if ver == "s577": j["sens_note"] = "민감도: 그래프만 queen 577"
    if ver == "s2": j["sens_note"] = "민감도: 80세 이상 비율 강제통제 없음"; j["forced"] = X(FORCED[:4])
    if ver == "sc": j["sens_note"] = "민감도: 비표준화(조) E(수검자 × 전국 연도 복부비만 율)"; j["offset_E_column"] = "E_crude"; j["offset_E_label"] = "crude E (examinees x national annual abdominal-obesity rate)"
    json.dump(j, open(os.path.join(HERE, f"sets_WAIST_{ver}.json"), "w"), ensure_ascii=False, indent=1)
j = make("WAISTA_Estd3w.csv", (2013, 2017), {"W1_2013-15": [2013, 2015], "W2_2016-17": [2016, 2017]}, 2016, LAB.format("2013-2017"), " [aux: earlier tabulation, 2013-2017]")
_ = "보조 기간 2013-17(2018 부분집합 연도 이전). COVID 단계 해당 없음."
json.dump(j, open(os.path.join(HERE, "sets_WAIST_aux.json"), "w"), ensure_ascii=False, indent=1)
for v in ["main", "s577", "s2", "sc", "aux"]:
    h = hashlib.sha256(open(os.path.join(HERE, f"sets_WAIST_{v}.json"), "rb").read()).hexdigest(); print(f"sets_WAIST_{v}.json sha256 {h}")
