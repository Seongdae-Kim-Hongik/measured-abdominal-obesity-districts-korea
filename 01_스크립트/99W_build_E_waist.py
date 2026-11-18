#!/usr/bin/env python3
#  분모 = N138 시군구 성별 '수검자수'(대사증후군 위험요인 표 수검자), 전국 율 = N139 성×연령 복부비만/수검자수.
#  기간: WAIST(주) 2019-2024, WAISTA(보조) 2013-2017, WAISTF(민감도) 2013-2024 전부. 2018 제외 근거 = 판정 게이트(그해 표 수검자 500만 = 일반검진 수검자의 33%, 지질검사 대상자 부분집합).
#  기준 입력 = 분석용 고정 복사본 SQLite region_year(mode=ro) chk__대사_복부비만_인원; 빈칸은 원표 N138 시군구 행(50 매핑, 코드 결합)으로, 세종은 원표 시도 머리행으로 채운다.
#  산출: 02_패널/WAIST_Estd3w.csv, WAISTA_Estd3w.csv, WAISTF_Estd3w.csv, 04_분석/WAIST/gate/00_WAIST_분자채움_세종_261118.csv
import os, sys, sqlite3, importlib.util, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); AN = os.path.join(ROOT, "04_분석"); PAN = os.path.join(ROOT, "02_패널")
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험")
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
def _load(nm, f):
    s = importlib.util.spec_from_file_location(nm, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
m38 = _load("m38", "38_build_Estd_all.py"); cw = _load("cw", "40_region_crosswalk.py"); m50 = _load("m50", "50_build_master_panel.py")
NFC = lambda s: unicodedata.normalize("NFC", str(s))
assert os.environ.get("ST_FBDZIP"), "ST_FBDZIP(창원 2023 교정 인구 폴더)를 지정"
YEARS = list(range(2011, 2025)); SEXES = ["남자", "여자"]
SCR = {"OTHS": ("chk__질환의심_기타질환", "N104", "기타질환", YEARS), "SUSP": ("chk__질환의심_실인원", "N104", "실인원", YEARS),
       "DXT": ("chk__유질환자_실인원", "N106", "실인원", YEARS), "TBT": ("chk__유질환자_폐결핵", "N106", "폐결핵", YEARS)}
MY = list(range(2013, 2025))
META = {"WAIST": ("chk__대사_복부비만_인원", "N139", "복부비만", "DT_35007_N138", "복부비만"), "HBP": ("chk__대사_높은혈압_인원", "N139", "높은혈압", "DT_35007_N138", "높은혈압"),
        "HGLU": ("chk__대사_높은혈당_인원", "N139", "높은혈당", "DT_35007_N138", "높은혈당"), "HTG": ("chk__대사_고중성지방_인원", "N139", "고중성지방혈증", "DT_35007_N138", "고중성지방혈증"),
        "LHDL": ("chk__대사_낮은HDL_인원", "N139", "낮은 HDL 콜레스테롤 혈증", "DT_35007_N138", "낮은HDL콜레스테롤혈증"), "MSPRE": ("chk__대사_주의군_인원", "N136", "주의군(1~2개)", "DT_35007_N135", "주의군(1~2개)")}
HI, CB, HT, IH = "허혈성 심장 질환 (I20-I25)", "뇌혈관 질환 (I60-I69)", "고혈압성 질환 (I10-I13)", "기타 심장 질환 (I26-I51)"
MORT = {}
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cols = ["chk__대사_복부비만_인원"]
RY = pd.read_sql("select year, fbd_region, " + ", ".join(f'"{c}"' for c in cols) + " from region_year where year between 2011 and 2024", con); RY["fbd_region"] = RY.fbd_region.map(NFC)
base = pd.read_sql("select year, key, fbd_region from disease_panel where tag='PERIO'", con); base["fbd_region"] = base.fbd_region.map(NFC); base["key"] = base.key.map(NFC)
PKEYS = set(base.key); assert len(base) == 3206
# ── 시군구 성×연령 인구(99U2 규칙) ──
BANDS16 = ["0-19"] + [f"{lo}-{lo+4}" for lo in range(20, 85, 5)] + ["85+"]; BANDS18 = [f"{lo}-{lo+4}" for lo in range(0, 85, 5)] + ["85+"]
SIDO_HDR = {k for k in cw.SIDO_STD if len(k) >= 3 and (k.endswith("시") or k.endswith("도"))}
FIVE = [f"{lo}-{lo+4}세" for lo in range(0, 85, 5)]; OLD85 = ["85-89세", "90-94세", "95-99세", "100세 이상"]
EXTRA = {("충청북도", "청원군"): "충청북도|청주시"}; rows = []
for y in YEARS:
    d = pd.read_csv(os.path.join(m38.FBDZIP, f"{y}.csv"), encoding="cp949", dtype=str)
    d["행정구역별"] = d["행정구역별"].map(NFC).str.strip(); d["연령별"] = d["연령별"].map(NFC).str.strip()
    for s in SEXES: d[s] = pd.to_numeric(d[s].str.replace(",", ""), errors="coerce")
    sido = None; city = None; blocks = (d["행정구역별"] != d["행정구역별"].shift()).cumsum()
    for _, g in d.groupby(blocks, sort=False):
        nm = g["행정구역별"].iat[0]
        if nm == "전국": continue
        if nm in SIDO_HDR:
            sido = nm; city = None
            if nm != "세종특별자치시": continue
            g = g.drop_duplicates("연령별")
        sg = nm.split("-")[-1]
        if sg.endswith("시"): city = sg
        elif sg.endswith("구") and city is not None and cw.sido_std(sido) not in ("서울시", "부산시", "대구시", "인천시", "광주시", "대전시", "울산시"): continue
        else: city = None
        key = EXTRA.get((cw.sido_std(sido), sg), cw.make_key(sido, sg))
        if key not in PKEYS and key.endswith("군") and key[:-1] + "시" in PKEYS: key = key[:-1] + "시"
        for s in SEXES:
            a = g.set_index("연령별")[s]
            if pd.isna(a.get("계", np.nan)): continue
            f = a.reindex(FIVE); o = a.reindex(OLD85).fillna(0); assert f.notna().all(), (y, nm, s)
            r = {"year": y, "sex": s, "key": NFC(key), **{b: f[b + "세"] for b in BANDS18[:-1]}, "85+": o.sum()}
            r["0-19"] = f["0-4세"] + f["5-9세"] + f["10-14세"] + f["15-19세"]; r["s0-19_adult"] = f["15-19세"]; rows.append(r)
POP = pd.DataFrame(rows).groupby(["year", "key", "sex"], as_index=False).sum(numeric_only=True)
cwn = POP[(POP.key == NFC(base[base.fbd_region == NFC("경상남도창원시")].key.iat[0])) & (POP.year == 2023)][BANDS18].sum().sum()
print(f"[99W] 창원 2023 인구 {cwn:,.0f} (정답 1,009,038)")
out = {}
# ── 대사 위험요인(N138 시군구 성별, N139 전국 성×16연령) ──
NATPOP16 = POP.groupby(["year", "sex"])[BANDS16].sum()
def nb_band(a):
    a = str(a).replace(" ", "")
    if a == "19세이하": return "0-19"
    if a == "85세이상": return "85+"
    if a.endswith("세") and "~" in a: lo, hi = a[:-1].split("~"); return f"{lo}-{hi}"
    return None
MY = list(range(2013, 2025))
L3 = pd.read_csv(os.path.join(PAN, "NHIS검진_시군구_연도_long.csv"), usecols=["year", "sido", "sigungu", "level", "sex", "category", "measure", "value", "tbl_id"], engine="pyarrow")
L3 = L3[(L3.tbl_id == "DT_35007_N138") & L3.year.isin(MY) & L3.sex.isin(SEXES) & (L3.measure == "인원")].copy()
LSJ = L3[(L3.level == "시도") & L3.sido.astype(str).str.contains("세종")]
L3 = L3[L3.level == "시군구"]
pr3 = L3[["sido", "sigungu"]].drop_duplicates(); mp3 = {(a, b): m50.map_region(a, b, PKEYS) for a, b in zip(pr3.sido, pr3.sigungu)}
L3["key"] = [mp3[(a, b)]["key"] for a, b in zip(L3.sido, L3.sigungu)]; L3["role"] = [mp3[(a, b)]["role"] for a, b in zip(L3.sido, L3.sigungu)]
L3 = L3[L3.key.notna()]; L3["key"] = L3.key.map(NFC); hp3 = L3[L3.role == "primary"].groupby(["key", "year", "category"]).size().index
L3 = L3[~((L3.role == "sub") & L3.set_index(["key", "year", "category"]).index.isin(hp3))]
SRC3 = L3.groupby(["category", "year", "key"]).value.sum(min_count=1)
SX3 = L3[L3.category == "수검자수"].pivot_table(index=["year", "key"], columns="sex", values="value", aggfunc="sum")
SJ = NFC("세종시세종시"); SJK = NFC(base[base.fbd_region == SJ].key.iat[0])
SJX = LSJ[LSJ.category == "수검자수"].pivot_table(index="year", columns="sex", values="value", aggfunc="sum")
SJC = LSJ[LSJ.category == "복부비만"].groupby("year").value.sum(min_count=1)
_have = [y for y in MY if (y, SJK) in SX3.index]; print("[99W] 세종 시군구 행 있는 연도", _have)
_add = SJX[~SJX.index.isin(_have)]
SX3 = pd.concat([SX3, pd.DataFrame({s: _add[s].values for s in SEXES}, index=pd.MultiIndex.from_arrays([_add.index, [SJK] * len(_add)], names=["year", "key"]))]).sort_index()
print("[99W] 세종 시도 머리행 수검자", SJX.sum(1).astype(int).to_dict(), "복부비만", SJC.astype(int).to_dict())
B = pd.read_csv(os.path.join(SRC, "DT_35007_N139_national_long.csv"), encoding="utf-8-sig", dtype={"grp_code": str}); B = B[(B.item == "인원") & B.year.isin(MY) & B.sex.isin(SEXES)].copy()
B["band"] = B.age.map(nb_band); B = B[B.band.notna()]
assert B.band.nunique() == 15, B.band.unique()
EXm = B[B.grp == "수검자수"].set_index(["year", "sex", "band"]).value.unstack()[BANDS16]
NUM = B[B.grp == "복부비만"].set_index(["year", "sex", "band"]).value.unstack()[BANDS16].fillna(0); RATE = NUM / EXm.loc[NUM.index]; UPm = EXm / NATPOP16.loc[EXm.index]
FILLLOG = []; col = "chk__대사_복부비만_인원"
P0 = base[base.year.isin(MY)].reset_index(drop=True)
P0 = P0.merge(RY[["year", "fbd_region", col]], on=["year", "fbd_region"], how="left", validate="one_to_one").rename(columns={col: "cases"})
sv = SRC3.loc["복부비만"].reindex(pd.MultiIndex.from_arrays([P0.year, P0.key])).values
both = P0.cases.notna().values & ~np.isnan(sv); dif = np.abs(P0.cases.values[both] - sv[both]); fill = P0.cases.isna().values & ~np.isnan(sv)
FILLLOG.append(dict(TAG="WAIST", 겹침칸=int(both.sum()), 일치칸=int((dif <= 2).sum()), 최대차=float(dif.max()) if both.any() else 0, 채운칸=int(fill.sum()),
                    채운곳="; ".join(f"{a}{b}" for a, b in P0.loc[fill, ["fbd_region", "year"]].values.tolist())))
P0.loc[fill, "cases"] = sv[fill]
sjm = (P0.fbd_region == SJ) & P0.cases.isna(); P0.loc[sjm, "cases"] = P0.loc[sjm, "year"].map(SJC).values
FILLLOG.append(dict(TAG="WAIST_세종", 겹침칸=0, 일치칸=0, 최대차=0, 채운칸=int(P0.loc[sjm, "cases"].notna().sum()), 채운곳="; ".join(f"{int(y)}:{int(v)}" for y, v in P0.loc[sjm, ["year", "cases"]].dropna().values.tolist())))
out = {}
for T, yrs in {"WAIST": list(range(2019, 2025)), "WAISTA": list(range(2013, 2018)), "WAISTF": MY}.items():
    P = P0[P0.year.isin(yrs)].reset_index(drop=True)
    S = SX3.reindex(pd.MultiIndex.from_arrays([P.year, P.key]))
    ok = P.cases.notna().values & S.notna().all(1).values & (S.min(1) > 0).values
    drop = P[~ok][["year", "fbd_region"]].values.tolist(); P = P[ok].reset_index(drop=True); S = S[ok]
    assert (P.cases <= S.sum(1).values).all()
    P["offset"] = S.sum(1).values; E = np.zeros(len(P))
    for s_ in SEXES:
        X = P[["year", "key"]].merge(POP[POP.sex == s_], on=["year", "key"], how="left", validate="one_to_one"); assert X[BANDS16].notna().all().all()
        raw = X[BANDS16].values * UPm.xs(s_, level="sex").loc[X.year.values].values; exam = raw * (S[s_].values / raw.sum(1))[:, None]
        E += (exam * RATE.xs(s_, level="sex").loc[X.year.values].values).sum(1)
    P["E_std"] = E * P.year.map(P.groupby("year").cases.sum()) / pd.Series(E).groupby(P.year.values).transform("sum").values
    P["E_crude"] = P.offset * P.year.map(P.groupby("year").cases.sum() / P.groupby("year").offset.sum())
    natc = NUM.groupby(level="year").sum().sum(1)
    print(f"[99W] {T}: 행 {len(P)}, 시군구 {P.fbd_region.nunique()}, {min(yrs)}-{max(yrs)}, 제외 {len(drop)}칸 {drop[:5]}, 합 {int(P.cases.sum()):,}, 시군구 합/전국 {(P.groupby('year').cases.sum()/natc.loc[yrs]).round(4).min()}~{(P.groupby('year').cases.sum()/natc.loc[yrs]).round(4).max()}, 0칸 {(P.cases==0).sum()}, 수검자 합/전국 {(P.groupby('year').offset.sum()/EXm.loc[yrs].groupby(level='year').sum().sum(1)).round(4).to_dict()}")
    out[T] = P
FL = pd.DataFrame(FILLLOG); print(FL.drop(columns="채운곳").to_string()); os.makedirs(os.path.join(AN, "WAIST", "gate"), exist_ok=True)
FL.to_csv(os.path.join(AN, "WAIST", "gate", "00_WAIST_분자채움_세종_261118.csv"), index=False, encoding="utf-8-sig")
for T, P in out.items():
    P[["year", "fbd_region", "offset", "cases", "E_std", "E_crude"]].to_csv(os.path.join(PAN, f"{T}_Estd3w.csv"), index=False, encoding="utf-8-sig")
