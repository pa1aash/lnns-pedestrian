"""Consistency audit: every number printed in the abstract, the contributions, the conclusions and the figure and
table captions must also appear, with the same value and precision, in the body section that reports it.

Text is taken from the LaTeX sources with every number macro replaced by its value from paper/numbers.tex;
\\cite, \\ref, \\eqref, \\label and comments are removed. A number is a decimal token (signs and ranges split, so
"0.85--0.93" gives 0.85 and 0.93; "10^{-3}" gives 10^-3).
  abstract, contributions, conclusions -> must appear in the body (Sects. 2-10 without captions, plus Table 1)
  caption of a figure or table         -> must appear in the body text of the section file that holds the float
                                          (or, for Fig. 1, the Introduction and Sect. 5), or in another caption of
                                          the same float's table body
Numbers that name a figure element only (panel radii, colour-scale ends, sample sizes of a plot) are listed too;
the report decides which are mismatches. Exit 1 when any number is missing.

Usage: python3 tools/check_number_consistency.py [-v]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "paper"
SEC = P / "sections"


def macros():
    m = {}
    for line in (P / "numbers.tex").read_text().splitlines():
        r = re.match(r"\\newcommand\{\\(\w+)\}\{(.*)\}\s*$", line)
        if r:
            m[r.group(1)] = r.group(2)
    return m


M = macros()


def expand(s):
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\(cite|ref|eqref|label|input|includegraphics|url|texttt)(\[[^\]]*\])?\{[^}]*\}", " ", s)
    s = re.sub(r"\\([A-Za-z]+)", lambda r: " " + M[r.group(1)] + " " if r.group(1) in M else r.group(0), s)
    s = re.sub(r"\\(ge|le|geq|leq|approx|sim|times|pm|mp)(?![A-Za-z])", " ", s)
    s = s.replace("\\ensuremath", "").replace("\\times10^{", " 10^").replace("10^{", "10^")
    return s


# caption numbers that describe the figure itself (display choices), not results; listed in P4_REPORT
ALLOWED_CAPTION = {"95": "interval level (Sect. 4.4) or plotted percentile band",
                   "2000": "number of agents drawn in the scatter (display subsample)",
                   "150": "colour-scale end of the margin shading", "1000": "colour-scale end of the wall-force shading"}

NUM = re.compile(r"(?<![A-Za-z_\\])(10\^-?\d+|\d+(?:\.\d+)?)")


def numbers(s):
    out = []
    for t in NUM.findall(s):
        out.append(t)
    return out


def body_tokens(text):
    return set(numbers(text))


def strip_floats(s):
    """Section text without figure/table environments and captions."""
    s = re.sub(r"\\begin\{(figure\*?|table\*?)\}.*?\\end\{\1\}", " ", s, flags=re.S)
    return s


def captions(s):
    out = []
    for env in re.finditer(r"\\begin\{(figure\*?|table\*?)\}(.*?)\\end\{\1\}", s, flags=re.S):
        body = env.group(2)
        i = body.find("\\caption{")
        if i < 0:
            continue
        j, depth = i + len("\\caption{"), 1
        k = j
        while depth and k < len(body):
            depth += {"{": 1, "}": -1}.get(body[k], 0)
            k += 1
        lab = re.search(r"\\label\{([^}]*)\}", body)
        out.append((lab.group(1) if lab else "?", body[j:k - 1]))
    return out


def main():
    verbose = "-v" in sys.argv
    files = sorted(SEC.glob("*.tex"))
    raw = {f.name: f.read_text() for f in files}
    # inline the tables into their section files
    for f in files:
        raw[f.name] = re.sub(r"\\input\{tables/(\w+)\}", lambda r: (P / "tables" / (r.group(1) + ".tex")).read_text(),
                             raw[f.name])
    fig1 = (ROOT / "figures" / "fig1_caption.tex").read_text()
    intro = raw["01_introduction.tex"]
    contrib = intro[intro.index("\\subsubsection{Contributions.}"):]
    intro_body = intro[:intro.index("\\subsubsection{Contributions.}")]
    body_files = [n for n in raw if n[:2] in {"02", "03", "04", "05", "06", "07", "08", "09", "10"}]
    body = " ".join(expand(strip_floats(raw[n])) for n in body_files)
    tab1 = expand((P / "tables" / "table1_params.tex").read_text())
    body_all = body + " " + tab1
    B = body_tokens(body_all)
    missing = []

    def check(name, text, ref_tokens, where):
        toks = numbers(expand(text))
        miss = [t for t in toks if t not in ref_tokens]
        if verbose:
            print(f"{name}: {len(toks)} numbers, {len(miss)} not in {where}")
        for t in miss:
            missing.append((name, t, where))

    abstract = raw["00_abstract.tex"]
    abstract = abstract[:abstract.index("\\keywords")]
    check("abstract", abstract, B, "body")
    check("contributions", contrib, B, "body")
    check("conclusions", raw["11_conclusions.tex"], B, "body")
    for n in body_files + ["01_introduction.tex"]:
        sec_body = expand(strip_floats(raw[n]))
        if n == "01_introduction.tex":
            sec_body = expand(intro_body) + " " + expand(strip_floats(raw["05_deadlock_physics.tex"]))
        for lab, cap in captions(raw[n]):
            text = fig1 if lab == "fig:hero" else cap
            if lab == "fig:hero":
                text = text[text.index("{", text.index("FigOneCaption")) + 1:]
            check(f"caption {lab}", text, body_tokens(sec_body) | (B if lab.startswith("tab:") else set()),
                  f"{n} body")
    # stricter pass: a sentence of the contributions or the conclusions that cites a section must find its numbers in
    # that section's file (body text, floats excluded)
    label_file = {}
    for n, t in raw.items():
        for lab in re.findall(r"\\label\{(sec:[^}]*)\}", t):
            label_file[lab] = n
    for name, text in (("contributions", contrib), ("conclusions", raw["11_conclusions.tex"])):
        for sent in re.split(r"(?<=[.;])\s+(?=[A-Z\\])", text):
            refs = re.findall(r"\\ref\{(sec:[^}]*)\}", sent)
            if not refs:
                continue
            ref_text = " ".join(expand(strip_floats(raw[label_file[r]])) for r in refs if r in label_file)
            for t in numbers(expand(sent)):
                if t not in body_tokens(ref_text):
                    missing.append((name + " (cited section)", t, ", ".join(refs)))
    for name, t, where in missing:
        if name.startswith("caption") and (t in ALLOWED_CAPTION or t in B):
            print(f"note {name}: {t} not in {where} but {ALLOWED_CAPTION[t] if t in ALLOWED_CAPTION else 'in the body'}")
            continue
        print(f"MISSING {name}: {t} (not in {where})")
    missing[:] = [x for x in missing if not (x[0].startswith("caption") and (x[1] in ALLOWED_CAPTION or x[1] in B))]
    print(f"{len(missing)} numbers not found")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
