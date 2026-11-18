import os, json, unicodedata, numpy as np, pandas as pd
from scipy.stats import spearmanr, norm
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.abspath(os.path.join(HERE, "..", "..")); AN = os.path.dirname(B); ROOT = os.path.dirname(AN); PAN = os.path.join(ROOT, "02_패널")
RS = lambda v="main": os.path.join(B, f"results_{v}"); NFC = lambda s: unicodedata.normalize("NFC", str(s)); EX = lambda f, v="main": os.path.exists(os.path.join(RS(v), f))
SHP = os.environ.get("ST_SHP", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "data", "boundary", "final.shp"))
VARS = {"walking_rate": "ext__walking_rate", "restaurant": "ext__restaurant_per10k", "instant_food": "ext__instant_food_per10k", "cars": "cars_per_capita",
        "high_risk_drinking": "ext__high_risk_drinking", "smoking_rate": "ext__smoking_rate", "stress": "perceived_stress_rate",
        "tertiary": "tertiary_educated_share", "basic_livelihood_rate": "basic_livelihood_rate", "screening_uptake": "ext__screening_uptake",
        "urban_population_share": "urban_population_share", "physicians_per_1000": "physicians_per_1000", "sex_ratio": "sex_ratio", "fiscal_independence": "fiscal_independence", "pop80_share": "pop80_share"}
HYP = list(VARS)[:10]; ROB = ["tertiary", "basic_livelihood_rate", "screening_uptake"]
def tab(f, v="main"):
    d = pd.read_csv(os.path.join(RS(v), f)); d["cov"] = d["cov"].astype(str); return d
def get(d, c):
    r = d[d["cov"] == c].iloc[0]; return [round(float(r.IRR), 3), round(float(r.lo), 3), round(float(r.hi), 3)]
N = {}
P = pd.read_csv(os.path.join(B, "panel_WAIST_main.csv")); P["fbd_region"] = P.fbd_region.map(NFC)
N["n_rows"] = len(P); N["n_districts"] = P.fbd_region.nunique(); N["cases_total_m"] = round(P.cases.sum() / 1e6, 2); N["exam_total_m"] = round(P.offset.sum() / 1e6, 1)
g = P.groupby("year"); N["rate"] = {int(k): round(100 * v, 2) for k, v in (g.cases.sum() / g.offset.sum()).items()}
N["exam"] = {int(k): round(v / 1e6, 2) for k, v in g.offset.sum().items()}
L = P.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
N["sir_min"], N["sir_max"] = round(L.min(), 2), round(L.max(), 2); N["sir_p10"], N["sir_p90"] = round(L.quantile(.1), 2), round(L.quantile(.9), 2); N["p90p10"] = round(L.quantile(.9) / L.quantile(.1), 2)
N["sir_top"] = [[r, round(v, 2)] for r, v in L.sort_values(ascending=False).head(10).items()]; N["sir_bottom"] = [[r, round(v, 2)] for r, v in L.sort_values().head(10).items()]
CR = P.groupby("fbd_region").apply(lambda d: 100 * d.cases.sum() / d.offset.sum(), include_groups=False); N["crude_p10_p90"] = [round(CR.quantile(.1), 1), round(CR.quantile(.9), 1)]
P["dens"] = P.population / (P.area_m2 / 1e6)
D = P.groupby("fbd_region").agg(ter=("tertiary_educated_share_raw", "mean"), bl=("basic_livelihood_rate_raw", "mean"), up=("ext__screening_uptake_raw", "mean"), dens=("dens", "mean"),
                                 p80=("pop80_share_raw", "mean"), ob=("obesity_rate_raw", "mean"), rest=("ext__restaurant_per10k_raw", "mean"))
for k in ("ter", "bl", "up", "dens", "p80", "ob", "rest"): N[f"rho_sir_{k}"] = round(spearmanr(L.reindex(D.index), D[k]).correlation, 2)
# 표 1 창별 기술
WIN = {"2019-2021": (2019, 2021), "2022-2024": (2022, 2024), "2019-2024": (2019, 2024)}
raw = {k: (VARS[k] + "_raw") for k in VARS}; assert all(c in P for c in raw.values()), [c for c in raw.values() if c not in P]
T1 = {}
for w, (a, b) in WIN.items():
    s = P[P.year.between(a, b)]; sw = s.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
    T1[w] = dict(n=len(s), cases=float(s.cases.sum()), exam=float(s.offset.sum()), rate=float(s.cases.sum() / s.offset.sum()), sir_med=float(sw.median()), sir_p10=float(sw.quantile(.1)), sir_p90=float(sw.quantile(.9)),
                 cov={k: [float(s[raw[k]].mean()), float(s[raw[k]].std())] for k in VARS})
N["T1"] = T1
mo = pd.read_csv(os.path.join(RS(), "S6_moran_year.csv")); N["moran_min"], N["moran_max"] = round(mo.moran_I.min(), 2), round(mo.moran_I.max(), 2)
Y = P.pivot_table(index="fbd_region", columns="year", values="SIR"); N["rho_2019_2024"] = round(spearmanr(Y[2019], Y[2024]).correlation, 2)
if EX("S12_persistence.csv"): N["kendall_w"] = round(float(pd.read_csv(os.path.join(RS(), "S12_persistence.csv")).iloc[0].kendall_W), 2)
# 전 기간(2013-24, 2018 포함) 전국 율과 보조 기간 순위 상관
F = pd.read_csv(os.path.join(PAN, "WAISTF_Estd3w.csv")); F["fbd_region"] = F.fbd_region.map(NFC); gf = F.groupby("year"); N["rate_full"] = {int(k): round(100 * v, 2) for k, v in (gf.cases.sum() / gf.offset.sum()).items()}
N["exam_full"] = {int(k): round(v / 1e6, 2) for k, v in gf.offset.sum().items()}
A = F[F.year.between(2013, 2017)]; LA = A.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E_std.sum(), include_groups=False); N["rho_aux_main"] = round(spearmanr(L, LA.reindex(L.index)).correlation, 2)
# Gi*(593 그래프, 자기 포함) — 6년 log SIR
import geopandas as gpd
G = open(os.path.join(B, "graph_593.graph")).read().split("\n"); nreg = int(G[0]); nb = {}
for line in G[1:]:
    t = line.split()
    if len(t) >= 2: nb[int(t[0])] = [int(x) for x in t[2:]]
area = pd.DataFrame({"fbd_region": gpd.read_file(SHP)["region"].values}); area["fbd_region"] = area.fbd_region.map(NFC); assert len(area) == nreg
id2r = dict(zip(range(1, nreg + 1), area.fbd_region))
x = np.log(L.reindex([id2r[i] for i in range(1, nreg + 1)]).values); assert not np.isnan(x).any(); xb, sd = x.mean(), x.std(); gi = []
for i in range(1, nreg + 1):
    w = np.zeros(nreg); w[i - 1] = 1; w[[j - 1 for j in nb.get(i, [])]] = 1; W = w.sum()
    gi.append(((w * x).sum() - xb * W) / (sd * np.sqrt((nreg * (w ** 2).sum() - W ** 2) / (nreg - 1))))
GI = pd.DataFrame({"fbd_region": [id2r[i] for i in range(1, nreg + 1)], "SIR": np.exp(x), "z": gi}); GI["p"] = 2 * norm.sf(GI.z.abs())
GI["cls"] = np.where((GI.p < 0.05) & (GI.z > 0), "hot", np.where((GI.p < 0.05) & (GI.z < 0), "cold", "other"))
S6 = pd.read_csv(os.path.join(RS(), "S6_spatial_RR.csv")); S6["fbd_region"] = S6.fbd_region.map(NFC); GI = GI.merge(S6[["fbd_region", "sigungu_cd"]], on="fbd_region", validate="one_to_one")
GI.to_csv(os.path.join(HERE, "gi_waist.csv"), index=False, encoding="utf-8-sig")
SIDO = {"서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "경기": "Gyeonggi", "강원": "Gangwon", "충청북": "Chungbuk",
        "충청남": "Chungnam", "전라북": "Jeonbuk", "전라남": "Jeonnam", "경상북": "Gyeongbuk", "경상남": "Gyeongnam", "제주": "Jeju"}
GI["sido"] = GI.fbd_region.map(lambda r: next(v for k, v in SIDO.items() if r.startswith(k)))
for c in ("hot", "cold"):
    s = GI[GI.cls == c]; N[f"gi_{c}"] = len(s); N[f"gi_{c}_sido"] = s.sido.value_counts().to_dict(); N[f"gi_{c}_sir_med"] = round(s.SIR.median(), 2)
    N[f"gi_{c}_gun"] = int(s.fbd_region.str.endswith("군").sum()); N[f"gi_{c}_gu"] = int(s.fbd_region.str.endswith("구").sum()); N[f"gi_{c}_si"] = len(s) - N[f"gi_{c}_gun"] - N[f"gi_{c}_gu"]
DD = D.join(GI.set_index("fbd_region").cls); N["hc"] = {c: {k: round(float(DD[DD.cls == c][k].median()), 2) for k in ("ter", "bl", "up", "dens", "p80", "ob")} for c in ("hot", "other", "cold")}
# 모형
M = tab("S3_main_IRR.csv"); N["main"] = {k: get(M, VARS[k]) for k in VARS}
Fm = pd.read_csv(os.path.join(RS(), "S3_main_fit.csv")).iloc[0]; N["waic_main"] = float(Fm.WAIC); N["phi"] = float(Fm.phi); N["n_hot_bym"] = int(Fm.n_hotspot); N["n_cold_bym"] = int(Fm.n_coldspot)
RM = pd.read_csv(os.path.join(RS(), "S8_residual_moran.csv")).set_index("quantity")
N["obs_moran"] = float(RM.loc["observed_logSIR_pooled", "moran_I"]); r_ = RM.loc["pearson_residual_area_mean"]; N["resid_moran"] = [float(r_.moran_I), float(r_.expected_I), float(r_.p_perm), str(r_.alternative)]
LK = pd.read_csv(os.path.join(RS(), "S1_likelihood.csv")); N["waic_forced"] = float(LK[LK.family == "nbinomial"].WAIC.iloc[0]); N["waic_forced_pois"] = float(LK[LK.family == "poisson"].WAIC.iloc[0])
hy = pd.read_csv(os.path.join(RS(), "S3_main_hyper.csv")); N["hyper"] = hy.round(3).values.tolist()
NC = tab("S3_negcontrol.csv"); N["nc"] = {c.replace("ext__", ""): get(NC, c) for c in NC["cov"]}
W = tab("S4_window_IRR.csv"); N["win"] = {f"{k}|{w}": get(W[W.window == w], VARS[k]) for k in VARS for w in W.window.unique()}
SC = pd.read_csv(os.path.join(B, "HM_setcompare_WAIST_main.csv")); N["setcomp"] = {r.set: float(r.WAIC) for r in SC.itertuples()}
HI = pd.read_csv(os.path.join(B, "HM_setcompare_IRR_WAIST_main.csv")); HI = HI[HI.set == "S1b_obesity_sensitivity"].rename(columns={"set": "s"})
N["s1b"] = {k: get(HI, VARS[k]) for k in VARS if (HI["cov"] == VARS[k]).any()}; N["s1b"]["obesity_rate"] = get(HI, "obesity_rate")
if EX("S7_multiverse_summary.csv"):
    MV = pd.read_csv(os.path.join(RS(), "S7_multiverse_summary.csv")); MV["cov"] = MV["cov"].astype(str)
    N["mv"] = {k: [round(float(MV[MV["cov"] == VARS[k]].cred_frac.iloc[0]), 3), round(float(MV[MV["cov"] == VARS[k]].sign_agree.iloc[0]), 3), int(MV[MV["cov"] == VARS[k]].n_specs.iloc[0])] for k in HYP if (MV["cov"] == VARS[k]).any()}
for t in ("KH_typeI", "KH_typeII", "KH_typeIII", "KH_typeIV"):
    f = "S9_typeI_IRR.csv" if t == "KH_typeI" else f"S43_part_{t}.csv"
    if EX(f): d = tab(f); N[t] = {k: get(d, VARS[k]) for k in VARS}; N[t + "_waic"] = float(d.WAIC.iloc[0])
if EX("S50_resid_moran_by_spec.csv"):
    d = pd.read_csv(os.path.join(RS(), "S50_resid_moran_by_spec.csv")); N["rm_spec"] = d.round(4).to_dict("records")
for a in ("E1_lag1", "E2_lag2", "D1_spatial_plus", "C4_sido_year_iid", "C1_poisson_lognormal", "G1_kchs_ma3", "H1_nco_METSC"):
    if EX(f"S41_part_{a}.csv"): d = tab(f"S41_part_{a}.csv"); N[a] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
for a in ("no_spatial", "iid_only", "icar_besag", "excl_2020_2021", "start_2020", "RSR", "pc_phi_flat", "main_queen"):
    if EX(f"S43_part_{a}.csv"): d = tab(f"S43_part_{a}.csv"); N[a] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
for f, key in (("S41_retention_by_cov.csv", "ret"), ("S41_evalues.csv", "evalue"), ("S42_variance_partition.csv", "vp"), ("S42_ppc.csv", "ppc"), ("S41_oos2024.csv", "oos")):
    if EX(f): N[key] = pd.read_csv(os.path.join(RS(), f)).round(4).to_dict("records")
for v in ("s577", "s2", "sc", "aux", "rep", "full"):
    if os.path.exists(os.path.join(RS(v), "S3_main_IRR.csv")):
        d = tab("S3_main_IRR.csv", v); N[v] = {k: get(d, VARS[k]) for k in VARS if (d["cov"] == VARS[k]).any()}
        f = pd.read_csv(os.path.join(RS(v), "S3_main_fit.csv")).iloc[0]; N[v + "_fit"] = dict(phi=float(f.phi), n=int(f.n_obs), waic=float(f.WAIC))
if EX("S41_part_bw_twoway.csv"):
    d = pd.read_csv(os.path.join(RS(), "S41_part_bw_twoway.csv")); d = d[d["cov"].astype(str).str.contains("__")]
    N["bw"] = {str(r.cov): [round(float(r.IRR), 3), round(float(r.lo), 3), round(float(r.hi), 3)] for r in d.itertuples(index=False)}; N["bw_waic"] = float(d.WAIC.iloc[0])
if EX("S50_region_slopes.csv"):
    RG = pd.read_csv(os.path.join(RS(), "S50_region_slopes.csv")); N["reg"] = {f"{r.covariate}|{r.region}": [r.IRR, r.lo, r.hi] for r in RG.itertuples()}
c2 = pd.read_csv(os.path.join(AN, "METSC", "panel_METSC.csv")).merge(pd.read_csv(os.path.join(PAN, "METSC_Estd.csv")), on=["year", "fbd_region"]); c2["fbd_region"] = c2.fbd_region.map(NFC)
S2 = c2.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E_std.sum(), include_groups=False); j = pd.concat([L, S2], axis=1).dropna(); N["rho_mets"] = [round(spearmanr(j[0], j[1]).correlation, 2), len(j)]
S6r = pd.read_csv(os.path.join(RS(), "S6_spatial_RR.csv")); N["rr_s"] = [round(S6r.RR.min(), 2), round(S6r.RR.max(), 2), round(S6r.RR.quantile(.1), 2), round(S6r.RR.quantile(.9), 2)]
N["n_hyp"] = 10; N["mv_n"] = 200
json.dump(N, open(os.path.join(HERE, "numbers_waist.json"), "w"), ensure_ascii=False, indent=1, default=float)
if __name__ == "__main__":
    print({k: N.get(k) for k in ("cases_total_m", "exam_total_m", "rate", "rate_full", "sir_p10", "sir_p90", "p90p10", "crude_p10_p90", "gi_hot", "gi_cold", "gi_hot_sido", "gi_cold_sido", "hc",
                                 "rho_2019_2024", "rho_aux_main", "moran_min", "moran_max", "obs_moran", "resid_moran", "rho_mets", "rho_sir_ter", "rho_sir_bl", "rho_sir_up", "rho_sir_dens", "rho_sir_ob", "rho_sir_rest", "sir_top", "sir_bottom")})
