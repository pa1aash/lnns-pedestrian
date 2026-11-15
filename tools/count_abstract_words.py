"""Word count of the printed abstract: number macros replaced by their values from paper/numbers.tex, LaTeX markup
removed, every whitespace-separated token that contains a letter or digit counted as a word (units such as "m" or
"s" count as words; a range "0.85--0.93" counts as one).

Usage: python3 tools/count_abstract_words.py [paper/sections/00_abstract.tex]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def macros():
    m = {}
    for line in (ROOT / "paper" / "numbers.tex").read_text().splitlines():
        r = re.match(r"\\newcommand\{\\(\w+)\}\{(.*)\}\s*$", line)
        if r:
            m[r.group(1)] = r.group(2)
    return m


def printed_text(tex):
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    a = tex.index(r"\begin{abstract}") + len(r"\begin{abstract}")
    b = tex.index(r"\keywords") if r"\keywords" in tex else tex.index(r"\end{abstract}")
    s = tex[a:b]
    M = macros()
    s = re.sub(r"\\([A-Za-z]+)(\\ |\s)?",
               lambda r: (M[r.group(1)] + (" " if r.group(2) else "")) if r.group(1) in M else r.group(0), s)
    s = s.replace(r"\beta", "β").replace(r"\ge", "≥")
    s = s.replace(r"\,", " ").replace("~", " ").replace("$", "")
    s = re.sub(r"\\(emph|textit|textbf|mathrm|rm)\b", "", s)
    s = re.sub(r"\\[a-zA-Z]+", "", s)
    s = re.sub(r"[{}\\^_]", "", s)
    return s


def count(s):
    return sum(1 for t in s.split() if re.search(r"[A-Za-z0-9]", t))


if __name__ == "__main__":
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper" / "sections" / "00_abstract.tex"
    s = printed_text(p.read_text())
    print(count(s))
