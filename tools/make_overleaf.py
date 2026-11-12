#!/usr/bin/env python3
r"""Build an Overleaf package of the paper: one main.tex with every \input inlined and every number
macro of paper/numbers.tex replaced by its literal value, refs.bib with only the cited entries
(unchanged from paper/refs.bib), the figures the build reads, and the unmodified llncs.cls and
splncs04.bst. The \pending macro and the \finaltrue switch stay in the preamble.

Usage (from the repository root, after `make paper`):  python3 tools/make_overleaf.py OUTDIR
"""
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
FIGS = os.path.join(ROOT, "figures")


def arg_end(s, i):
    """s[i] == '{'; index just past the matching '}'."""
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise SystemExit("make_overleaf: unbalanced braces")


def strip_comment_lines(s):
    """Drop lines that are only a comment; keep trailing-% line joins intact."""
    return "\n".join(ln for ln in s.splitlines() if not re.match(r"^\s*%", ln))


def read_tex(path):
    return strip_comment_lines(open(path).read()).rstrip("\n") + "\n"


def main(out):
    tex = open(os.path.join(PAPER, "main.tex")).read()

    # number macros: \newcommand{\Name}{value}, one per line
    nums = {}
    for ln in open(os.path.join(PAPER, "numbers.tex")):
        m = re.match(r"\\newcommand\{\\([A-Za-z]+)\}\{", ln)
        if m:
            k = m.end() - 1
            nums[m.group(1)] = ln[k + 1:arg_end(ln, k) - 1]
    tex = tex.replace("\\input{numbers}\n", "")

    # Fig. 1: the hero tikzpicture with its overlay, and the caption macro
    hero = read_tex(os.path.join(FIGS, "fig1_hero.tex"))
    hero = re.sub(r"\\providecommand\{\\(figdir|heroimage|overlayfile)\}\{[^\n]*\n", "", hero)
    hero = hero.replace("\\heroimage", "figures/fig1_hero.png")
    hero = hero.replace("\\input{\\overlayfile}%", read_tex(os.path.join(FIGS, "fig1_overlay.tex")).rstrip("\n"))
    cap = open(os.path.join(FIGS, "fig1_caption.tex")).read()
    m = re.search(r"\\newcommand\{\\FigOneCaption\}\{", cap)
    caption = cap[m.end():arg_end(cap, m.end() - 1) - 1]

    def inline(text, base):
        while True:
            m = re.search(r"\\input\{([^}]*)\}", text)
            if not m:
                return text
            name = m.group(1)
            if name.endswith("fig1_hero.tex"):
                body = hero
            else:
                f = os.path.normpath(os.path.join(base, name))
                if not os.path.splitext(f)[1]:
                    f += ".tex"
                body = inline(read_tex(f), base)
            # a file ends a line (its last line may end in a comment), as TeX's \input does
            nl = "" if text[m.end():m.end() + 1] == "\n" else "\n"
            text = text[:m.start()] + body.rstrip("\n") + nl + text[m.end():]

    tex = inline(tex, PAPER)
    # the caption file is guarded by \IfFileExists in the introduction
    m = re.search(r"\\IfFileExists\{../figures/fig1_caption.tex\}", tex)
    if m:
        a = arg_end(tex, m.start() + len("\\IfFileExists"))
        b = arg_end(tex, a)
        c = arg_end(tex, b)
        tex = tex[:m.start()] + tex[c:].lstrip("\n")
    tex = tex.replace("\\caption{\\FigOneCaption}", "\\caption{" + caption + "}")
    if "FigOneCaption" in tex:
        raise SystemExit("make_overleaf: Fig. 1 caption macro left")

    # number macros -> literal values: "\Name\ " -> "v ", "\Name{}" -> "v", "\Name" + spaces -> "v"
    pat = re.compile(r"\\([A-Za-z]+)(\{\}|\\ | +)?")

    def sub(m):
        name, tail = m.group(1), m.group(2) or ""
        if name not in nums:
            return m.group(0)
        v = nums[name]
        return v + (" " if tail == "\\ " else "")

    tex = pat.sub(sub, tex)
    left = sorted({n for n in re.findall(r"\\([A-Za-z]+)", tex) if n in nums})
    if left:
        raise SystemExit(f"make_overleaf: number macros left: {left}")

    tex = tex.replace("../figures/", "figures/")
    if "../" in tex:
        raise SystemExit("make_overleaf: relative path left: " + str(sorted(set(re.findall(r"\.\./\S*", tex)))))

    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        p = os.path.join(out, f)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    open(os.path.join(out, "main.tex"), "w").write(tex)

    # figures read by the repository build
    fls = open(os.path.join(PAPER, "main.fls")).read()
    figs = sorted({os.path.normpath(os.path.join(PAPER, ln.split(" ", 1)[1])) for ln in fls.splitlines()
                   if ln.startswith("INPUT ") and ln.lower().endswith((".pdf", ".png", ".jpg"))
                   and os.path.normpath(os.path.join(PAPER, ln.split(" ", 1)[1])).startswith(FIGS + "/")})
    os.makedirs(os.path.join(out, "figures"))
    for f in figs:
        shutil.copy2(f, os.path.join(out, "figures", os.path.basename(f)))
    used = set(re.findall(r"figures/([^}\s]+)", tex))
    if used != {os.path.basename(f) for f in figs}:
        raise SystemExit(f"make_overleaf: figures referenced {sorted(used)} vs read {figs}")

    # refs.bib: only the cited entries, verbatim
    aux = open(os.path.join(PAPER, "main.aux")).read()
    cited = []
    for grp in re.findall(r"\\citation\{([^}]*)\}", aux):
        for k in grp.split(","):
            if k not in cited:
                cited.append(k)
    bib = open(os.path.join(PAPER, "refs.bib")).read()
    starts = [m.start() for m in re.finditer(r"^@", bib, re.M)] + [len(bib)]
    entries = {}
    for a, b in zip(starts, starts[1:]):
        e = bib[a:b].rstrip() + "\n"
        k = re.match(r"@\w+\{([^,\s]+),", e)
        if k:
            entries[k.group(1)] = e
    miss = [k for k in cited if k not in entries]
    if miss:
        raise SystemExit(f"make_overleaf: cited keys missing from refs.bib: {miss}")
    keep = [k for k in entries if k in cited]          # refs.bib order
    open(os.path.join(out, "refs.bib"), "w").write("\n".join(entries[k] for k in keep))

    for f in ("llncs.cls", "splncs04.bst"):
        shutil.copy2(os.path.join(PAPER, "llncs", f), os.path.join(out, f))

    open(os.path.join(out, "README.txt"), "w").write(
        "Compile main.tex with pdfLaTeX and BibTeX (Overleaf: Compiler pdfLaTeX; locally: latexmk -pdf main.tex).\n"
        "Files: main.tex (the whole paper), refs.bib (cited entries only), figures/, llncs.cls, splncs04.bst (unmodified).\n"
        "Packages beyond llncs come with TeX Live (Overleaf included); cite prints grouped citations sorted and compressed.\n"
        "Three author items are marked \\pending{...} and print in red: the Zenodo DOI (Data and Code Availability),\n"
        "the Acknowledgments and the Disclosure of Interests, all in the credits block just before the references.\n"
        "For the final build uncomment \\finaltrue in the preamble: any \\pending left then stops the compile with an error.\n")
    print(f"overleaf: {out}: main.tex ({len(tex.splitlines())} lines), {len(figs)} figures, {len(keep)} bib entries")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(os.path.abspath(sys.argv[1]))
