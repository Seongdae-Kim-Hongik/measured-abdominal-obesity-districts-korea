import os, re, datetime, subprocess
from docx import Document
from docx.shared import Pt, Cm
import content_waist as C
from build_orcp_waist import TITLE, ZENODO, ADDRESS
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out")
N = C.N; W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_orcp.txt")).read().split()); th = C.th; tc = C.tc
assert ZENODO.startswith("10.5281/zenodo.")
_d = datetime.date.today(); cl = [f"{_d:%B} {_d.day}, {_d.year}", "The Editor-in-Chief", "Obesity Research & Clinical Practice", "",
      "Dear Editor,",
      f"Please find enclosed the manuscript entitled \"{TITLE}\" by Seongdae Kim, for consideration as an Original Research Article in Obesity Research & Clinical Practice.",
      f"District-level obesity data in Korea are mostly self-reported. Korea's national general health screening, however, measures waist circumference in every attendee and publishes the number above the abdominal obesity cut-offs of the Korean Society for the Study of Obesity by district each year. Using these measurements for all {N['n_districts']} Korean districts from 2019 to 2024 ({N['cases_total_m']:.1f} million attendances with abdominal obesity), the study maps where measured abdominal obesity is more common than expected after standardization for sex and age and asks which district characteristics follow it. Abdominal obesity was modestly lower in districts with more university-educated adults, an association that held across most space-time interaction and spatial confounding models, whereas food outlets, registered cars, walking, and survey-reported behaviors showed no consistent association. The published screening table was checked against attendance counts before modeling, and all alternative model specifications are reported.",
      "The work fits the journal's interest in the epidemiology of obesity in the Asia Oceania region: it uses a nationwide, measured, and annually updated source of waist circumference data to describe the geography of abdominal obesity among screening attendees in Korea.",
      "The manuscript is original research, has not been published previously, and is not under consideration for publication elsewhere; the author has approved its submission.",
      f"The text contains {th(int(W['body_words']))} words, with an abstract of {int(W['abstract_words'])} words, two tables, two figures, and {W['refs']} references. Highlights, a graphical abstract, and supplementary material are provided. The analysis code is openly available on Zenodo (https://doi.org/{ZENODO}).",
      "Thank you for considering this manuscript.", "", "Sincerely,", "",
      "Seongdae Kim, PhD", ADDRESS, "Email: kimsd@hongik.ac.kr"]
d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.0
for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)
gap = False
for t in cl:
    if t == "": gap = True; continue
    p = d.add_paragraph(t)
    if gap: p.paragraph_format.space_before = Pt(10); gap = False
d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Cover Letter"; d.core_properties.comments = ""
fp = os.path.join(OUT, "Cover_Letter.docx"); d.save(fp)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_waist_cl", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
txt = subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and not re.search(r"(?i)funding|competing|overlap|previously submitted|Chun|reviewer", txt), "문체·금지 항목"
pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout).group(1)); assert pages == 1, pages
open(os.path.join(OUT, "Cover_Letter_paste.txt"), "w").write("\n\n".join(t for t in cl if t))
print("saved", fp)
