#  ★Spatial+·RSR은 결과와 무관하게 10개 변수 전부 싣는다(S3). 잔차 Moran은 양측·기대값과 함께(S5).
import os, json, re
import pandas as pd
from build_orcp_waist import TX, put_table, OUT, N, to_pdf, TITLE, th
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.abspath(os.path.join(HERE, "..", "..")); RS = os.path.join(B, "results_main"); ROOT = os.path.dirname(os.path.dirname(B))
VARS = {"walking_rate": "ext__walking_rate", "restaurant": "ext__restaurant_per10k", "instant_food": "ext__instant_food_per10k", "cars": "cars_per_capita", "high_risk_drinking": "ext__high_risk_drinking",
        "smoking_rate": "ext__smoking_rate", "stress": "perceived_stress_rate", "tertiary": "tertiary_educated_share", "basic_livelihood_rate": "basic_livelihood_rate", "screening_uptake": "ext__screening_uptake"}
LAB = {"walking_rate": "Walking", "restaurant": "Restaurants", "instant_food": "Instant food", "cars": "Cars", "high_risk_drinking": "High-risk drinking", "smoking_rate": "Smoking",
       "stress": "Stress", "tertiary": "Tertiary education", "basic_livelihood_rate": "Livelihood security", "screening_uptake": "Screening uptake"}
f3 = lambda r: f"{r[0]:.3f} ({r[1]:.3f}-{r[2]:.3f})" if r else "\u2013"
def row(d, c):
    x = d[d["cov"].astype(str) == c]
    return f3([float(x.IRR.iloc[0]), float(x.lo.iloc[0]), float(x.hi.iloc[0])]) if len(x) else "\u2013"
def en(s): return re.sub(r"(\d)-(\d)", "\\1\u2013\\2", s)
def t1():
    E, R = N["exam_full"], N["rate_full"]
    N099 = {2013: 11.38, 2014: 12.30, 2015: 13.21, 2016: 13.71, 2017: 13.99, 2018: 15.08, 2019: 16.10, 2020: 14.54, 2021: 16.95, 2022: 17.23, 2023: 17.46, 2024: 17.52}
    rows = [[str(y), f"{E[str(y)]:.2f}", f"{N099[y]:.2f}", f"{E[str(y)]/N099[y]:.3f}", f"{R[str(y)]:.1f}", "Excluded (lipid-tested subset)" if y == 2018 else ("Principal" if y >= 2019 else "Earlier period")] for y in range(2013, 2025)]
    return ("Supplementary Table S1. Attendee totals of the metabolic syndrome risk factor table compared with all general screening attendees, Korea, 2013-2024",
            ["Year", "Table attendees, million", "General screening attendees, million", "Ratio", "Abdominal obesity, %", "Use"], rows,
            "Table attendees: DT_35007_N138/N139; general screening attendees: DT_35007_N099. Province-level ratios were 1.050\u20131.078 in 2013\u20132017, 0.31\u20130.36 in 2018, and 0.98\u20131.00 from 2019. The waist cut-offs (\u226590 cm in men, \u226585 cm in women) did not change. "
            "Sejong (province row only) was included for all years, and 1 district-year missing from the analysis copy (Bucheon, 2016) was filled from the source table; the sum of districts equaled the national total in every year.")
S2 = [("General restaurants", "Food and mobility", "General restaurants per 10,000 residents", "Local administrative licensing data", "+"),
      ("Instant food businesses", "Food and mobility", "Instant food manufacturing and processing businesses per 10,000 residents", "Local administrative licensing data", "+"),
      ("Registered cars", "Food and mobility", "Registered cars per resident; Sejong imputed by the yearly mean", "KOSIS e-local indicators", "+"),
      ("Walking rate", "Food and mobility", "Adults walking at least 30 minutes on at least 5 days a week, age-standardized, %", "Community Health Survey", "\u2212"),
      ("High-risk drinking", "Risk behaviors and stress", "Adults drinking 7 or more standard drinks (women 5) at least twice a week, age-standardized, %", "Community Health Survey", "+"),
      ("Current smoking", "Risk behaviors and stress", "Adults currently smoking cigarettes, age-standardized, %", "Community Health Survey", "+"),
      ("Perceived stress", "Risk behaviors and stress", "Adults reporting much stress in daily life, age-standardized, %", "Community Health Survey", "+"),
      ("Tertiary education", "Socioeconomic position", "Adults with a junior college degree or higher, %", "Population and Housing Census via KOSIS", "\u2212"),
      ("Basic livelihood security", "Socioeconomic position", "Basic livelihood security recipients per 100 residents; implausible 2021-2023 values set to missing and interpolated", "Ministry of Health and Welfare via KOSIS", "+"),
      ("Screening uptake", "Screening", "First-stage general health screening attendees as a share of those eligible, %", "National Health Insurance Service via KOSIS", "\u2212"),
      ("Self-reported obesity", "Sensitivity only", "Adults with self-reported body mass index of 25 kg/m\u00b2 or more, age-standardized, %", "Community Health Survey", "+"),
      ("Urban population share", "Fixed adjustment", "Residents in urban zones, % of population", "KOSIS", "\u2013"), ("Physicians", "Fixed adjustment", "Physicians per 1,000 residents", "KOSIS e-local indicators", "\u2013"),
      ("Sex ratio", "Fixed adjustment", "Men per 100 women", "Resident registration", "\u2013"), ("Fiscal autonomy", "Fixed adjustment", "Fiscal autonomy ratio, %", "KOSIS", "\u2013"),
      ("Aged 80 years or older", "Fixed adjustment", "Residents aged 80 years or older, %", "Resident registration", "\u2013"),
      ("Hit-and-run crashes", "Negative control", "Hit-and-run crashes per 100 traffic crashes", "KOSIS e-local indicators", "none"),
      ("Traffic culture index", "Negative control", "Traffic culture index score", "Korea Transportation Safety Authority via KOSIS", "none"),
      ("Fires", "Negative control", "Fires per 10,000 residents", "National Fire Agency via KOSIS", "none")]
def t2():
    return ("Supplementary Table S2. District characteristics, definitions, sources, and expected direction", ["Characteristic", "Group", "Definition", "Source", "Expected"], [[a, b, en(c), d, e] for a, b, c, d, e in S2],
            "Expected direction for abdominal obesity. Survey items not collected in a year were interpolated within districts. All characteristics were standardized to 1 SD of district-years. KOSIS, Korean Statistical Information Service.")
SPECS = [("Principal model", "S3_main_IRR.csv", "main"), ("Knorr-Held type I", "S9_typeI_IRR.csv", "main"), ("Knorr-Held type II", "S43_part_KH_typeII.csv", "main"),
         ("Knorr-Held type III", "S43_part_KH_typeIII.csv", "main"), ("Knorr-Held type IV", "S43_part_KH_typeIV.csv", "main"), ("Spatial+", "S41_part_D1_spatial_plus.csv", "main"),
         ("Restricted spatial regression", "S43_part_RSR.csv", "main"), ("Province-by-year effects", "S41_part_C4_sido_year_iid.csv", "main"), ("Lagged 1 year", "S41_part_E1_lag1.csv", "main"),
         ("Lagged 2 years", "S41_part_E2_lag2.csv", "main"), ("Excluding 2020-2021", "S43_part_excl_2020_2021.csv", "main"), ("Poisson-lognormal", "S41_part_C1_poisson_lognormal.csv", "main"),
         ("ICAR district effect", "S43_part_icar_besag.csv", "main"), ("Independent district effect only", "S43_part_iid_only.csv", "main"), ("No district effect", "S43_part_no_spatial.csv", "main"),
         ("Queen graph (577 pairs)", "S3_main_IRR.csv", "s577"), ("Without the age-80 adjustment", "S3_main_IRR.csv", "s2"), ("Unstandardized expected counts", "S3_main_IRR.csv", "sc"),
         ("2020-2024 only", "S43_part_start_2020.csv", "main"), ("2013-2017", "S3_main_IRR.csv", "aux"), ("2013-2024 including 2018", "S3_main_IRR.csv", "full"), ("Principal model, second fit", "S3_main_IRR.csv", "rep")]
def t3(keys, part):
    rows = []
    for lab, f, v in SPECS:
        p = os.path.join(B, f"results_{v}", f)
        if not os.path.exists(p): continue
        d = pd.read_csv(p); rows.append([lab] + [row(d, VARS[k]) for k in keys])
    return (f"Supplementary Table S3{part}. Rate ratios per 1 SD (95% CrI) of all 10 characteristics under alternative specifications", ["Specification"] + [LAB[k] for k in keys], rows,
            "Each row changes one element of the principal model; all specifications are shown regardless of direction or credibility. Restricted spatial regression constrains the district effect to be orthogonal to the district means of the characteristics, which narrows CrIs. CrI, credible interval; ICAR, intrinsic conditional autoregressive.")
def t4():
    rows = [["__H__", "Between-district and within-district components"]]
    for k in ("tertiary", "basic_livelihood_rate", "screening_uptake"):
        c = VARS[k]; rows.append([f"  {LAB[k]}", f3(N["bw"][c + "__between"]), f3(N["bw"][c + "__within"])])
    rows.append(["__H__", "Comparison outcome: metabolic syndrome at the same screening"])
    for k in ("tertiary", "basic_livelihood_rate", "screening_uptake", "walking_rate"): rows.append([f"  {LAB[k]}", f3(N["H1_nco_METSC"][k]), "\u2013"])
    rows.append(["__H__", "Region-specific slopes (principal model with region interactions)"])
    for k in ("tertiary", "basic_livelihood_rate", "screening_uptake"):
        for rg, lab in (("Capital", "Capital region"), ("Yeongnam", "Yeongnam"), ("Honam", "Honam"), ("Chungcheong", "Chungcheong"), ("Gangwon_Jeju", "Gangwon and Jeju")):
            x = N["reg"].get(f"{VARS[k]}|{rg}")
            if x: rows.append([f"  {LAB[k]}, {lab}", f3(x), "\u2013"])
    rows.append(["__H__", "Self-reported obesity added (sensitivity)"])
    for k in ("tertiary", "basic_livelihood_rate", "screening_uptake"): rows.append([f"  {LAB[k]}", f3(N["s1b"][k]), "\u2013"])
    rows.append(["  Self-reported obesity", f3(N["s1b"]["obesity_rate"]), "\u2013"])
    rows.append(["__H__", "Negative-control exposures"])
    for k, l in (("hit_and_run_rate", "Hit-and-run crashes"), ("traffic_culture_index", "Traffic culture index"), ("fires_per_10000", "Fires")): rows.append([f"  {l}", f3(N["nc"][k]), "\u2013"])
    rows.append(["__H__", "E-values (CrI limit)"])
    for e in N["evalue"]: rows.append([f"  {LAB[next(k for k, v in VARS.items() if v == e['cov'])]}", f"{e['E_point']:.2f} ({e['E_limit']:.2f})", "\u2013"])
    return ("Supplementary Table S4. Between- and within-district components, comparison outcome, sensitivity model, negative controls, and E-values", ["Characteristic or model", "RR (95% CrI)\nor between", "Within"], rows,
            "Rate ratios per 1 SD. Between = district mean; within = deviation from the district mean (two-way centered). The comparison outcome was standardized in the same way (228 districts; Sejong not available). CrI, credible interval.")
def t5():
    rows = [[r["spec"].replace("_", " "), str(r["n_cov"]), f"{r['WAIC']:,.1f}", f"{r['resid_moran_I']:.3f}", f"{r['expected_I']:.4f}", "<.001" if r["p_perm"] < 0.001 else f"{r['p_perm']:.3f}"] for r in N["rm_spec"]]
    return ("Supplementary Table S5. Residual spatial autocorrelation by model specification", ["Specification", "Covariates", "WAIC", "Moran's I", "Expected I", "2-sided P"], rows,
            "Moran's I of district-mean Pearson residuals on the 593-pair contact graph with 2-sided permutation tests (999 permutations; P listed as <.001 when no permutation was as extreme, so the attainable bound is P \u2264 .002). Values above the expected value indicate remaining positive autocorrelation; none of the specifications showed values below it. WAICs in this table come from the residual-diagnostic refits and may differ from the main text in the first decimal. Posterior predictive check of the principal model: 95% interval coverage " + f"{100*N['ppc'][0]['coverage95']:.1f}%, PIT Kolmogorov-Smirnov P = {N['ppc'][0]['pit_ks_p']:.3f}.")
def t6():
    W = pd.read_csv(os.path.join(RS, "S4_window_IRR.csv")); M = pd.read_csv(os.path.join(RS, "S3_main_IRR.csv"))
    rows = [[LAB[k], row(M, c), row(W[W.window == "W1_2019-21"], c), row(W[W.window == "W2_2022-24"], c)] for k, c in VARS.items()]
    mv = N["mv"]; rows2 = [[LAB[k], f"{100*mv[k][0]:.0f}", f"{100*mv[k][1]:.0f}", str(mv[k][2])] for k in VARS]
    return ("Supplementary Table S6. Principal model by period and covariate-subset (multiverse) results", ["Characteristic", "2019-2024", "2019-2021", "2022-2024"], rows,
            "Rate ratios per 1 SD (95% CrI). Multiverse (200 random subsets with the 5 fixed adjustments), credible % / sign agreement % / subsets containing: " +
            "; ".join(f"{LAB[k]} {r[1]}/{r[2]}/{r[3]}" for k, r in zip(VARS, rows2)) + ".")
if __name__ == "__main__":
    J = TX(cite="bracket"); J.para("<b>Supplementary material</b>"); J.para(TITLE)
    K = list(VARS)
    for t in (t1(), t2(), t3(K[:4], "a"), t3(K[4:7], "b"), t3(K[7:], "c"), t4(), t5(), t6()):
        J.page_break(); put_table(J, t, fs=7 if "S3" in t[0] else 8)
    J.doc_title = "Supplementary material"; p = os.path.join(OUT, "Supplementary_Material.docx"); J.save(p); to_pdf(p); print("supplementary ok")
