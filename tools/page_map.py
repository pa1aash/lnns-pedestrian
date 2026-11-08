#!/usr/bin/env python3
"""Per-section page usage of paper/main.pdf.

Copies paper/ to a temporary directory, places a position marker (\\pdfsavepos, written at
shipout with the page number) before every
\\input{sections/...}, before the bibliography and at the end of the document, compiles with
latexmk, and reports each part's length in pages (fractional, measured on the text block).
Floats count where LaTeX places them, so a figure set on a later page is charged to the part
whose text is running there. With --pinned every figure and table is set in place ([H], float.sty)
on one tall page (no page breaks), so each part is charged its own floats and no break gaps; lengths
are divided by the real text height. The pinned total ignores page-fill losses.
The paper itself is not modified.

Usage: python3 tools/page_map.py [--pinned] [--json out.json]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SP_PER_PT = 65536.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--pinned", action="store_true")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as td:
        if os.environ.get("PAGEMAP_KEEP"):
            td = os.environ["PAGEMAP_KEEP"]; shutil.rmtree(td, ignore_errors=True); os.makedirs(td)
        work = Path(td) / "paper"
        shutil.copytree(ROOT / "paper", work, ignore=shutil.ignore_patterns("submission", "main.pdf"))
        (Path(td) / "figures").symlink_to(ROOT / "figures")
        if a.pinned:
            for f in list((work / "sections").glob("*.tex")) + list((work / "tables").glob("*.tex")):
                t = f.read_text()
                t = re.sub(r"\\begin\{(figure|table)\*?\}(\[[^\]]*\])?", r"\\begin{\1}[H]", t)
                t = re.sub(r"\\end\{(figure|table)\*\}", r"\\end{\1}", t)
                f.write_text(t)
        tex = (work / "main.tex").read_text()
        if a.pinned:
            tex = tex.replace("\\begin{document}", "\\usepackage{float}\n"
                              "\\newdimen\\pmrealth\\pmrealth=\\textheight\n"
                              "\\AtBeginDocument{\\typeout{PAGEMAP realth=\\the\\pmrealth}}\n"
                              "\\textheight=15000pt\\paperheight=15600pt\\pdfpageheight=\\paperheight\n"
                              "\\begin{document}", 1)
        names = []

        def mark(label):
            names.append(label)
            return f"\\pmmark{{{len(names)}}}"
        pre = ("\\newwrite\\pmfile\\immediate\\openout\\pmfile=\\jobname.pmap\n"
               "\\newcount\\pmabs\\pmabs=1\\AddToHook{shipout/after}{\\global\\advance\\pmabs by 1}\n"
               "\\def\\pmmark#1{\\pdfsavepos\\write\\pmfile{#1 \\the\\pmabs\\space\\the\\pdflastypos}}\n"
               "\\AtBeginDocument{\\typeout{PAGEMAP textheight=\\the\\textheight}"
               "\\typeout{PAGEMAP paperheight=\\the\\paperheight}"
               "\\typeout{PAGEMAP topskip=\\the\\dimexpr 1in+\\voffset+\\topmargin+\\headheight+\\headsep\\relax}}\n")
        tex = tex.replace("\\begin{document}", pre + "\\begin{document}", 1)
        tex = re.sub(r"\\input\{(sections/[^}]+)\}",
                     lambda m: mark(m.group(1).split("/")[-1]) + "\n" + m.group(0), tex)
        tex = tex.replace("\\bibliographystyle", mark("references") + "\n\\bibliographystyle", 1)
        endmark = mark("END") if a.pinned else "\\clearpage" + mark("END") + "\\null"
        tex = tex.replace("\\end{document}", endmark + "\n\\end{document}", 1)
        (work / "main.tex").write_text(tex)
        for _ in range(2):
            subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-quiet", "main.tex"], cwd=work,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log = (work / "main.log").read_text(errors="replace")
        pmap = (work / "main.pmap").read_text()
    dims = {k: float(v) for k, v in re.findall(r"PAGEMAP (\w+)=([\d.]+)pt", log)}
    top = dims["paperheight"] - dims["topskip"]          # y of the text block top (pt from bottom)
    th = dims.get("realth", dims["textheight"])
    pos = {}
    for lab, page, y in re.findall(r"(\d+) (\d+) (-?\d+)", pmap):
        y = float(y) / SP_PER_PT
        frac = (top - y) / th if a.pinned else min(max((top - y) / th, 0.0), 1.0)
        pos[int(lab)] = int(page) - 1 + frac
    rows = []
    for i, name in enumerate(names[:-1], start=1):
        rows.append({"part": name, "start": round(pos[i], 2), "pages": round(pos[i + 1] - pos[i], 2)})
    total = pos[len(names)]
    # pages of the title block (before the first marker)
    rows.insert(0, {"part": "title", "start": 0.0, "pages": round(pos[1], 2)})
    for r in rows:
        print(f"{r['part']:<22} {r['pages']:5.2f}")
    print(f"{'total':<22} {total:5.2f}")
    if a.json:
        Path(a.json).write_text(json.dumps({"parts": rows, "total": total}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
