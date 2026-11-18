#  ORCP 규정(논문_마스터자료/99_복부비만지리_ORCP/00_저널가이드/ORCP_가이드요약_261118.md): 본문 ≤3,500단어, 표+그림 ≤5, 참고 ≤35, 구조 초록 ≤250, 키워드 1-7, 하이라이트 3-5개(≤85자), 이중 익명(제목면 별도), 절 번호,
#   번호 인용 대괄호 등장순, LTWA 약어, 표 편집 가능·세로선 음영 없음(원고 끝), 그림 별도 파일, 지도 면책 문구, AI 고지 절은 참고문헌 앞, CRediT.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from jkms_engine import JKMS
import content_waist as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_waist.json"), encoding="utf-8")); th = C.th; tc = C.tc
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
FUNDING = "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."
CREDIT = "Seongdae Kim: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Visualization, Writing - original draft, Writing - review and editing."
COI = "The author declares that there are no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper."
AI_HEAD = "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"
AI_STATEMENT = "During the preparation of this work the author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. After using these tools, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article."
def data_full(): return f"All source data are publicly available aggregate statistics cited in the Methods. The analysis code and the scripts that generate every number, table, and figure are openly available on Zenodo (https://doi.org/{ZENODO}) under the MIT License. The processed district-year data are available from the author on reasonable request."

def cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def strip(t): return re.sub(r"\s*\[@[^\]]+\]", "", t)
def all_keys():
    src = open(os.path.join(HERE, "content_waist.py"), encoding="utf-8").read() + open(os.path.join(HERE, "content_waist_intro_methods.py"), encoding="utf-8").read(); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")})
KEYS = all_keys(); _miss = [k for k in KEYS if k not in REFS]; assert not _miss, _miss
KEEP = {"Philadelphia", "Race-Ethnicity", "Space", "Time", "Tract-Level", "Korean", "South", "Society", "Study", "Obesity", "Guidelines", "Management", "Mendelian", "Sociodemographic", "Adults", "Korea", "Korean", "Canadian", "Gyeonggi", "Australian", "Diabetes", "Obesity", "Lifestyle", "Ambulatory", "Care", "Cholesterol", "Korea:", "NHIS", "LDL", "HDL", "Nutrition", "Examination", "Surveys", "European", "Asia", "Asian", "Medicare", "Medicaid", "Roemer's", "Japan", "Massachusetts", "OECD", "Bayesian", "Laplace", "Spatial+", "Besag", "STROBE", "Medical", "Aid", "National", "Health", "Insurance", "Service", "Community", "Survey", "Andersen's", "United", "States", "Gaussian", "Markov", "Moran", "I", "Wiley", "South"}
def sent(t):
    w = t.split(" "); caps = sum(1 for x in w[1:] if x[:1].isupper())
    if len(w) < 4 or caps < 0.5 * (len(w) - 1): return t
    out = [w[0]]
    for x in w[1:]:
        core = x.strip("(),:;.?[]\"'")
        keep = core in KEEP or core.isupper() or any(c.isdigit() for c in core) or out[-1].endswith((":", "?"))
        out.append(x if keep else x[:1].lower() + x[1:])
    t2 = " ".join(out)
    for a_, b_ in (("medical Aid", "Medical Aid"), ("Medical care", "medical care"), ("Health care", "health care"), ("Medical service", "medical service"), ("National health insurance", "national health insurance")): t2 = t2.replace(a_, b_)
    return t2
def short_pages(p):
    m = re.fullmatch(r"(\d+)-(\d+)", p or "")
    if not m: return p
    a, b = m.groups()
    if len(a) == len(b):
        i = 0
        while i < len(a) - 1 and a[i] == b[i]: i += 1
        b = b[i:]
    return f"{a}-{b}"
def vref(k):   # Elsevier 번호(JAMDA 예시): Van der Geer J, Hanraads JAJ, Lupton RA. Title. J Sci Commun 2020;163:51-9. https://doi.org/...
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}, {r['url']}; {r['year']} [accessed {r['accessed']}]."
    if r["type"] == "book": return f"{r['authors'][0]}. {r['title']}. {r['publisher']}; {r['year']}." + (f" https://doi.org/{r['doi']}." if r.get("doi") else "")
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:6]) + ", et al"
    t = sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a}. {t} {r['journal']} {r['year']}"
    if r.get("vol"): s += f";{r['vol']}" + (f":{short_pages(r['pages'])}" if r.get("pages") else "")
    return s + "." + (f" https://doi.org/{r['doi']}." if r.get("doi") else "")

class TX(JKMS):
    raw = False; table_bold = True
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

COVLAB = [("Food and mobility environment", [("restaurant", "General restaurants per 10,000"), ("instant_food", "Instant food businesses per 10,000"), ("cars", "Registered cars per capita"), ("walking_rate", "Walking rate, %")]),
          ("Risk behaviors and stress", [("high_risk_drinking", "High-risk drinking, %"), ("smoking_rate", "Current smoking, %"), ("stress", "Perceived stress, %")]),
          ("Socioeconomic position and screening", [("tertiary", "Tertiary education, %"), ("basic_livelihood_rate", "Basic livelihood security recipients, %"), ("screening_uptake", "Screening uptake, %")]),
          ("Fixed adjustments", [("urban_population_share", "Urban population share, %"), ("physicians_per_1000", "Physicians per 1,000"), ("sex_ratio", "Sex ratio, men per 100 women"), ("fiscal_independence", "Fiscal autonomy, %"), ("pop80_share", "Aged 80 years or older, %")])]
def table1():
    T = N["T1"]; cols = ["2019-2021", "2022-2024", "2019-2024"]
    rows = [["__H__", "Abdominal obesity at screening"], ["  District-years, n"] + [th(T[c]["n"]) for c in cols], ["  Attendances, million"] + [f"{T[c]['exam']/1e6:.1f}" for c in cols],
            ["  Attendees with abdominal obesity, million"] + [f"{T[c]['cases']/1e6:.2f}" for c in cols], ["  Abdominal obesity, % of attendees"] + [f"{100*T[c]['rate']:.1f}" for c in cols],
            ["  District ratio, median<sup>a</sup>"] + [f"{T[c]['sir_med']:.2f}" for c in cols], ["  District ratio, 10th-90th percentile<sup>a</sup>"] + [f"{T[c]['sir_p10']:.2f}-{T[c]['sir_p90']:.2f}" for c in cols]]
    for g, vs in COVLAB:
        rows.append(["__H__", f"{g}, mean (SD)"])
        for v, lab in vs:
            mx = max(abs(T[c]["cov"][v][0]) for c in cols); dp = 0 if mx >= 100 else (2 if mx < 5 else 1)
            rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:,.{dp}f} ({T[c]['cov'][v][1]:,.{dp}f})" for c in cols])
    foot = ("<sup>a</sup>Observed over expected attendees with abdominal obesity (waist circumference \u226590 cm in men, \u226585 cm in women; indirect standardization for sex and 15 age groups), summed over the period. "
            "Means and SDs are over district-years. Survey-based rates are age-standardized rates from the Community Health Survey.")
    return ("Table 1. Abdominal obesity at health screening and district characteristics by period, Korea, 2019-2024", ["Characteristic"] + cols, rows, foot)
def table2():
    rows = []
    for g, vs in COVLAB:
        rows.append(["__H__", g])
        for v, lab in vs:
            lab = re.sub(r", %$|, men per 100 women$", "", lab)
            m = N["main"][v]; mv = N["mv"].get(v); k4 = N["KH_typeIV"].get(v); sp = N["D1_spatial_plus"].get(v); py = N["C4_sido_year_iid"].get(v)
            f = lambda x: f"{x[0]:.3f} ({x[1]:.3f}-{x[2]:.3f})" if x else "\u2013"
            rows.append([f"  {lab}", f(m), f"{100*mv[0]:.0f}" if mv else "\u2013", f(k4), f(sp), f(py)])
    foot = ("Rate ratios per 1 SD with 95% credible intervals (CrIs). Principal model: negative binomial with a Besag-York-Molli\u00e9 2 district effect and random-walk and independent year effects, "
            f"10 characteristics and 5 fixed adjustments ({th(N['n_rows'])} district-years). \u2013, forced into every model (no subset share). "
            "<sup>a</sup>Share of the 200 covariate-subset models containing the characteristic in which the CrI excluded 1. "
            "<sup>b</sup>Principal model plus a Knorr-Held type IV space-time interaction. "
            "<sup>c</sup>Spatial+ (characteristics replaced by residuals from a spatial smooth). "
            "<sup>d</sup>Principal model plus independent province-by-year effects. Restricted spatial regression and other specifications are in Supplementary Table S3.")
    return ("Table 2. District characteristics and abdominal obesity at health screening, Korea, 2019-2024",
            ["Characteristic", "Principal model\nRR (95% CrI)", "Subsets\ncredible, %<sup>a</sup>", "Knorr-Held IV\nRR (95% CrI)<sup>b</sup>", "Spatial+\nRR (95% CrI)<sup>c</sup>", "Province-by-year\nRR (95% CrI)<sup>d</sup>"], rows, foot)

FIGCAP = {
 1: ("Abdominal obesity at health screening across Korean districts",
     "(A) Ratio of observed to expected attendees with abdominal obesity (indirect standardization for sex and 15 age groups) summed over 2019-2024; solid outlines, Getis-Ord Gi* hot spots, and dashed outlines, cold spots (P < .05). "
     "(B) National share of screening attendees with abdominal obesity, 2013-2024; the 2018 value covers only attendees who also had lipid tests and was not analyzed. "
     "(C) Median share with tertiary education, basic livelihood security recipients, screening uptake, population density, and self-reported obesity in hot-spot, other, and cold-spot districts, each relative to the highest group. "
     "Map lines delineate study areas and do not necessarily depict accepted national boundaries."),
 2: ("Rate ratios of abdominal obesity per 1 SD of 3 district characteristics across model specifications",
     "Points and lines show rate ratios and 95% credible intervals from the principal model; models with Knorr-Held type II and type IV space-time interactions; Spatial+; restricted spatial regression; a model with province-by-year effects; "
     "the between-district and within-district components; the 2013-2017 period; and metabolic syndrome from the same screening as a comparison outcome."),
}
def foot_row(J, text, sz=8, ls=12):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=False); foot_row(J, t[3]); J.counting = c

ACK = "None."
def body(J, anon=True):
    J.counting = True; sec = 0
    def H1(t):
        nonlocal sec; sec += 1; J.head(f"{sec}. {t}", 1); return sec
    H1("Introduction")
    for p in C.INTRO: J.para(cites(p), indent=True)
    n = H1("Subjects, materials and methods")
    for i, x in enumerate(C.METHODS, 1):
        J.head(f"{n}.{i}. {x[0]}", 2)
        for p in x[1:]: J.para(cites(p), indent=True)
    n = H1("Results")
    for i, x in enumerate(C.results(), 1):
        J.head(f"{n}.{i}. {x[0]}", 2)
        for p in x[1:]: J.para(cites(p), indent=True)
    n = H1("Discussion"); k = 0
    for p in C.DISCUSSION:
        if p.startswith("### "): k += 1; J.head(f"{n}.{k}. {p[4:].strip()}", 2); continue
        J.para(cites(p), indent=True)
    H1("Conclusions")
    for p in C.CONCLUSION: J.para(cites(p), indent=True)
    J.counting = False
    J.head("CRediT authorship contribution statement", 1); J.para("[Removed for anonymized review; provided on the title page]" if anon else CREDIT)
    for h, t in (("Funding", FUNDING), ("Data availability", data_anon() if anon else data_full()), (AI_HEAD, AI_STATEMENT)):
        J.head(h, 1); J.para(t)
def data_anon(): return "All source data are publicly available aggregate statistics cited in the Methods. The analysis code and the scripts that generate every number, table, and figure are openly available in a public repository (link provided on the title page to preserve anonymity) under the MIT License."
def build(bw=0, aw=0):
    J = TX(cite="bracket")
    J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    J.para("<b>Article type:</b> Research Paper", before=6)
    J.para(f"<b>Word counts:</b> abstract {aw} words; text {th(bw)} words. <b>Tables and figures:</b> 2 tables and 2 figures. <b>References:</b> {len(KEYS)}.", before=6)
    J.page_break(); J.head("Abstract", 1)
    for h, t in C.ABSTRACT: J.para(f"<b>{h}:</b> {t}")
    J.para(f"<b>Keywords:</b> {C.KEYWORDS}", before=6)
    J.page_break(); body(J, anon=True)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for n, k in enumerate(J.cites, 1): s = f"[{n}] {vref(k)}"; rl.append(s); J.para(s)
    J.raw = False
    J.page_break(); J.head("Figure legends", 1)
    for k in sorted(FIGCAP): t, c = FIGCAP[k]; J.para(f"<b>Figure {k}.</b> {t}. {c}")
    J.page_break(); put_table(J, table1()); J.page_break(); put_table(J, table2(), fs=8)
    return J, rl
def title_page(bw, aw):
    J = TX(cite="bracket")
    J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    J.para("Seongdae Kim<sup>a</sup>", before=12); J.para(f"<sup>a</sup>{ADDRESS}")
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}.", before=6)
    J.para(f"<b>Word counts:</b> abstract {aw} words; text {th(bw)} words. <b>Tables and figures:</b> 2 tables and 2 figures. <b>References:</b> {len(KEYS)}.", before=6)
    from content_waist_intro_methods import IRB_FULL
    for h, t in (("Ethics approval", IRB_FULL), ("CRediT authorship contribution statement", CREDIT), ("Declaration of competing interest", COI), ("Funding", FUNDING), ("Data availability", data_full()), (AI_HEAD, AI_STATEMENT), ("Acknowledgements", ACK)):
        J.head(h, 1); J.para(t)
    return J

def docx_bw(path):
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    return len(t[t.find("\n1. Introduction\n"):t.find("\nCRediT authorship contribution statement\n")].split())
def to_pdf(p): subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_waist_orcp", "--convert-to", "pdf", "--outdir", os.path.dirname(p), p], check=True, capture_output=True)

HIGHLIGHTS = ["Screening waist measurements mapped abdominal obesity across Korean districts",
              "Districts with more university-educated adults had less abdominal obesity",
              "The education gradient held in most space-time and spatial confounding models",
              "Food outlets, registered cars, and survey behaviors showed no consistent link",
              "The counts describe screening attendees, not all residents of each district"]

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_anonymized.docx")
    aw = sum(len(t.split()) for _, t in C.ABSTRACT) + sum(len(h.split()) for h, _ in C.ABSTRACT); assert aw <= 250, aw
    J, rl = build(); J.doc_title = "Manuscript"; J.save(p); bw = docx_bw(p)
    J, rl = build(bw, aw); J.doc_title = "Manuscript"; J.save(p); assert docx_bw(p) == bw, bw
    assert bw <= 3500 and len(KEYS) <= 35, (bw, len(KEYS))
    to_pdf(p)
    T = title_page(bw, aw); T.doc_title = "Title page"; tp = os.path.join(OUT, "Title_Page.docx"); T.save(tp); to_pdf(tp)
    assert 3 <= len(HIGHLIGHTS) <= 5 and all(len(h) <= 85 for h in HIGHLIGHTS), [len(h) for h in HIGHLIGHTS]
    K = TX(cite="bracket"); K.para("<b>Highlights</b>")
    for h in HIGHLIGHTS: K.para("\u2022 " + h)
    K.doc_title = "Highlights"; K.save(os.path.join(OUT, "Highlights.docx"))
    K = TX(cite="bracket"); K.para("<b>Declaration of interests</b>"); K.para(f"Manuscript: {TITLE}")
    K.para("\u2612 The author declares that there are no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.")
    K.doc_title = "Declaration of interests"; K.save(os.path.join(OUT, "Declaration_of_Interests.docx"))
    open(os.path.join(OUT, "wordcount_orcp.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\ntitle_words={len(TITLE.split())}\n")
    open(os.path.join(OUT, "references.txt"), "w").write("\n".join(rl))
    print(f"body {bw} | abstract {aw} | refs {len(KEYS)} | title words {len(TITLE.split())}")
