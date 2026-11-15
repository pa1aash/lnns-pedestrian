"""Check that every number of the deleted tables and dropped columns still appears in the paper text.

The deleted tables are the signature, observed-response, matched-noise and matched-bias tables of the commit given
as REF (default HEAD before the merge; pass a commit as argv[1]). Every number-macro they used must either be used
in the current paper sources (sections, tables, figure captions) or have its rendered value in the built PDF text.
Literal numbers typed into the deleted tables (not macros) are checked against the PDF text.

Usage: python tools/check_dropped_numbers.py [REF]   (run after `make paper`)
Exit 0 when nothing is missing.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
DELETED = ["paper/tables/table2_signatures.tex", "paper/tables/table3_observed.tex",
           "paper/tables/table4_noise.tex", "paper/tables/table5_bias.tex"]

def git_show(path):
    return subprocess.run(["git", "show", f"{REF}:{path}"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout

def strip_comments(s):
    return re.sub(r"(?<!\\)%.*", "", s)

numbers = {}
for line in (ROOT / "paper/numbers.tex").read_text().splitlines():
    m = re.match(r"\\newcommand\{\\(\w+)\}\{(.*)\}\s*$", line)
    if m:
        numbers[m.group(1)] = m.group(2)

def render(v):
    v = re.sub(r"\\ensuremath\{(.*)\}", r"\1", v)
    v = v.replace("\\times10^{", "×10^").replace("^{", "^").replace("}", "")
    return v.lstrip("=")

current = ""
for p in list((ROOT / "paper/sections").glob("*.tex")) + list((ROOT / "paper/tables").glob("*.tex")) + \
        list((ROOT / "figures").glob("*caption*.tex")):
    current += strip_comments(p.read_text())
used_now = set(re.findall(r"\\([A-Za-z]+)", current))

pdftext = subprocess.run(["pdftotext", str(ROOT / "paper/main.pdf"), "-"], capture_output=True, text=True,
                         check=True).stdout
pdftext = re.sub(r"-\n", "", pdftext)
pdfnorm = pdftext.replace("−", "-").replace("\u2212", "-")

missing = []
checked = 0
for path in DELETED:
    src = strip_comments(git_show(path))
    body = src[src.find("\\begin{tabular"):] if "\\begin{tabular" in src else src
    for name in sorted(set(re.findall(r"\\([A-Za-z]+)", body))):
        if name not in numbers:
            continue
        checked += 1
        if name in used_now:
            continue
        val = render(numbers[name])
        if val and val.replace("−", "-") in pdfnorm:
            continue
        missing.append((path, name, numbers[name]))
    # literal numbers typed into the table body (outside macros)
    lit = re.sub(r"\\[A-Za-z]+(\{[^}]*\})?", " ", body)
    for num in sorted(set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", lit))):
        checked += 1
        if num not in pdfnorm:
            missing.append((path, "literal", num))

print(f"checked {checked} numbers from {len(DELETED)} deleted tables")
for m in missing:
    print("MISSING", *m)
sys.exit(1 if missing else 0)
