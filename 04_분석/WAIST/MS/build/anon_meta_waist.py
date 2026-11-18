# anon_meta_waist.py — 이중 익명용: 익명 원고·보충·하이라이트 docx 메타데이터(저자·수정자) 비우고 PDF 재생성(2026-11-19).
import os, subprocess
from docx import Document
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
for f in ["Manuscript_anonymized.docx", "Supplementary_Material.docx", "Highlights.docx"]:
    p = os.path.join(OUT, f); d = Document(p); cp = d.core_properties
    cp.author = ""; cp.last_modified_by = ""; cp.comments = ""; cp.keywords = ""; cp.subject = ""; d.save(p)
    if f != "Highlights.docx": subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_waist_anon", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)
    r = subprocess.run(["pdfinfo", p.replace(".docx", ".pdf")], capture_output=True, text=True).stdout if f != "Highlights.docx" else ""
    print(f, repr(Document(p).core_properties.author), [l for l in r.split("\n") if l.startswith(("Author", "Creator"))])
