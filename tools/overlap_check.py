#!/usr/bin/env python3
"""Report word runs shared between the conference paper and the draft.

Extracts text from ref/camera_ready_SIMULTECH2026.pdf (pdftotext) and from the drafted
section files (LaTeX commands, math, citations, references, comments, figure/table
environments stripped), normalises both to lower-case word sequences, and prints every
maximal shared run of at least --min words (default 8), longest first. Runs made only of
standard technical phrases (STOP_PHRASES) are dropped. The conference reference list is
cut off before matching. Exit status 1 if any run reaches --fail words (default 10).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "ref" / "camera_ready_SIMULTECH2026.pdf"
SECTIONS = ROOT / "paper" / "sections"

# phrases that are standard technical names, not prose (lower case, word-normalised)
STOP_PHRASES = [
    "optimal reciprocal collision avoidance",
    "social force model",
    "time to collision",
    "forschungszentrum julich",
]


def words(text):
    text = text.lower().replace("’", "'").replace("ü", "u")
    text = re.sub(r"-\s*\n\s*", "", text)          # hyphenation across lines
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)


def conference_words():
    txt = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True, text=True, check=True).stdout
    m = re.search(r"\n\s*REFERENCES\s*\n", txt)
    if m:
        txt = txt[:m.start()]
    return words(txt)


def strip_latex(s):
    s = re.sub(r"(?<!\\)%.*", "", s)
    for env in ("figure\\*?", "table\\*?", "equation", "align\\*?"):
        s = re.sub(r"\\begin\{%s\}.*?\\end\{%s\}" % (env, env), " ", s, flags=re.S)
    s = re.sub(r"\$\$.*?\$\$|\$[^$]*\$", " ", s, flags=re.S)
    s = re.sub(r"\\(cite|ref|eqref|label|input|pending|includegraphics)\*?(\[[^\]]*\])?\{[^}]*\}", " ", s)
    s = re.sub(r"\\the\\numexpr[^\\]*\\relax", " ", s)
    s = re.sub(r"\\[A-Za-z]+\*?", " ", s)          # remaining commands (incl. number macros)
    s = s.replace("~", " ").replace("{", " ").replace("}", " ")
    return s


def draft_words():
    files = sorted(SECTIONS.glob("*.tex"))
    return words(" ".join(strip_latex(f.read_text()) for f in files))


def shared_runs(a, b, n):
    """Maximal runs of >= n consecutive words of b that also occur consecutively in a."""
    grams = {tuple(a[i:i + n]) for i in range(len(a) - n + 1)}
    text_a = " " + " ".join(a) + " "
    runs, i = [], 0
    while i <= len(b) - n:
        if tuple(b[i:i + n]) in grams:
            j = i + n
            while j < len(b) and (" " + " ".join(b[i:j + 1]) + " ") in text_a:
                j += 1
            runs.append(b[i:j])
            i = j
        else:
            i += 1
    return runs


def is_stop(run):
    s = " ".join(run)
    for p in STOP_PHRASES:
        s = s.replace(p, "")
    return len(s.split()) < 4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=8)
    ap.add_argument("--fail", type=int, default=10)
    a = ap.parse_args()
    runs = [r for r in shared_runs(conference_words(), draft_words(), a.min) if not is_stop(r)]
    runs.sort(key=len, reverse=True)
    for r in runs:
        print(f"{len(r):3d}  {' '.join(r)}")
    longest = len(runs[0]) if runs else 0
    print(f"overlap_check: {len(runs)} shared runs of >= {a.min} words; longest {longest}")
    return 1 if longest >= a.fail else 0


if __name__ == "__main__":
    sys.exit(main())
