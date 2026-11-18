import os
from build_orcp_waist import TX, put_table, OUT, TITLE
J = TX(cite="bracket"); J.para("<b>Ethical Statement</b>"); J.para(f"Manuscript: {TITLE}")
J.para("This ecological study used only published, aggregated statistics (national health screening statistics, resident registration statistics, the Community Health Survey, and administrative indicators by district). No individual-level data were accessed, and no participant could be identified. The study was approved by the institutional review board of the author's institution, which also approved its continuing review and waived informed consent because only published aggregate statistics were used; the name of the board, the approval numbers, and the dates are given on the title page to preserve anonymity during review. The study was conducted in accordance with the Declaration of Helsinki.")
J.doc_title = "Ethical Statement"; J.save(os.path.join(OUT, "Ethical_Statement.docx"))
J = TX(cite="bracket"); J.para("<b>Author Agreement</b>"); J.para(f"Manuscript: {TITLE}")
J.para("The author confirms that this manuscript is original, has not been published elsewhere, and is not under consideration for publication elsewhere. The sole author has contributed to and approved the final version, agrees to its submission to Obesity Research & Clinical Practice, and is accountable for its content.")
J.doc_title = "Author Agreement"; J.save(os.path.join(OUT, "Author_Agreement.docx"))
S = [("Title and abstract", "1", "Design (ecological panel study) indicated in the abstract Methods; informative, balanced abstract", "Abstract"),
     ("Background/rationale", "2", "Scientific background and rationale", "1. Introduction"),
     ("Objectives", "3", "Objectives stated", "1. Introduction, last paragraph"),
     ("Study design", "4", "Ecological panel study of districts, 2019-2024", "2.1"),
     ("Setting", "5", "All Korean districts; data years and sources", "2.1"),
     ("Participants", "6", "Units are districts; outcome among general health screening attendees", "2.1"),
     ("Variables", "7", "Outcome (waist circumference cut-offs), 10 characteristics, 5 adjustments, negative controls, comparison outcome", "2.1-2.2; Supplementary Table S2"),
     ("Data sources/measurement", "8", "Published statistics with table identifiers; checks against attendance counts", "2.1; Supplementary Tables S1-S2"),
     ("Bias", "9", "Attendance selection, residual confounding, negative controls, spatial confounding models", "2.3; 4.4"),
     ("Study size", "10", "229 districts x 6 years (1,374 district-years)", "2.1; 3.1"),
     ("Quantitative variables", "11", "Standardized to 1 SD; indirect standardization for sex and 15 age groups", "2.1-2.2"),
     ("Statistical methods", "12", "Bayesian spatio-temporal negative binomial models, sensitivity analyses, missing data handling", "2.3; Supplementary Tables S3-S6"),
     ("Participants (results)", "13", "District-years analyzed; no exclusions in the principal period", "3.1; Table 1"),
     ("Descriptive data", "14", "Characteristics by period", "Table 1"),
     ("Outcome data", "15", "Attendances with abdominal obesity and national shares", "3.1; Fig. 1"),
     ("Main results", "16", "Rate ratios with 95% credible intervals per 1 SD", "3.2; Table 2"),
     ("Other analyses", "17", "Robustness, components, comparison outcome, negative controls", "3.3; Fig. 2; Supplementary Tables S3-S6"),
     ("Key results", "18", "Summary of key results", "4. Discussion, first paragraph"),
     ("Limitations", "19", "Ecological design, attendance selection, standardization, residual confounding", "4.4"),
     ("Interpretation", "20", "Cautious interpretation", "4.1-4.3; 5"),
     ("Generalisability", "21", "Applies to screening attendees, not all residents", "4.3-4.4; 5"),
     ("Funding", "22", "No specific funding", "Funding section")]
from docx import Document as _Doc
from docx.shared import Pt
D = _Doc(); D.add_paragraph().add_run("Reporting Guidelines Checklist (STROBE, adapted for an ecological study)").bold = True; D.add_paragraph(f"Manuscript: {TITLE}")
T = D.add_table(rows=1, cols=4); T.style = "Table Grid"
for c, h in zip(T.rows[0].cells, ["Item", "No.", "Recommendation addressed", "Location in manuscript"]): c.text = h
for x in S:
    r = T.add_row().cells
    for c, v in zip(r, x): c.text = v
for row in T.rows:
    for c in row.cells:
        for p_ in c.paragraphs:
            for r_ in p_.runs: r_.font.size = Pt(9)
D.add_paragraph("Locations refer to the numbered sections, tables, and figures of the anonymized manuscript and the Supplementary material.")
D.save(os.path.join(OUT, "Reporting_Guidelines_Checklist_STROBE.docx"))
from docx import Document
for f in ("Ethical_Statement.docx", "Author_Agreement.docx", "Reporting_Guidelines_Checklist_STROBE.docx"):
    p = os.path.join(OUT, f); d = Document(p); d.core_properties.author = ""; d.core_properties.last_modified_by = ""; d.save(p)
print("ok")
