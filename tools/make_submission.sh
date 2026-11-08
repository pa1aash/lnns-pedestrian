#!/usr/bin/env bash
# Build paper/submission/: one self-contained main.tex (every \input and the compiled
# bibliography inlined), the figures it uses, and the unmodified llncs.cls and splncs04.bst.
# Then compile a copy of the folder on its own in a temporary directory and report the
# number of \pending items left. Run from the repository root (make submission).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAPER="$ROOT/paper"
OUT="$PAPER/submission"

# 1. build the paper (also produces main.bbl and main.fls)
(cd "$PAPER" && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null) \
  || { echo "make_submission: paper build failed (see paper/main.log)"; exit 1; }

# 2. latexpand (TeX Live); BasicTeX installs lack it, so fall back to TEXMFHOME
LATEXPAND="$(command -v latexpand || true)"
if [ -z "$LATEXPAND" ]; then
  TH="$(kpsewhich -var-value TEXMFHOME 2>/dev/null || true)"
  [ -n "$TH" ] && [ -x "$TH/scripts/latexpand/latexpand" ] && LATEXPAND="$TH/scripts/latexpand/latexpand"
fi
[ -n "$LATEXPAND" ] || { echo "make_submission: latexpand not found (tlmgr install latexpand)"; exit 1; }

# 3. clean the output folder, keeping the tracked README
mkdir -p "$OUT"
find "$OUT" -mindepth 1 ! -name README.md -exec rm -rf {} +

EXPANDED="$(mktemp)"
trap 'rm -f "$EXPANDED"' EXIT
(cd "$PAPER" && "$LATEXPAND" --expand-bbl main.bbl main.tex > "$EXPANDED")

# inline what latexpand cannot (macro paths, \IfFileExists), rewrite figure paths, copy files
python3 - "$PAPER" "$EXPANDED" "$OUT" <<'PY'
import os, re, shutil, sys

paper, expanded, out = sys.argv[1:4]
text = open(expanded).read()
FIGDIR = "../figures/"

def arg_end(s, i):
    """s[i] == '{'; return the index just past the matching '}'."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "\\":
            continue
        if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return j + 1
    raise SystemExit("make_submission: unbalanced braces")

def path_macros(s):
    """Simple path macros defined in s, with \\providecommand / \\newcommand / \\renewcommand semantics."""
    defs = {}
    for kind, name, val in re.findall(r"\\(provide|new|renew)command\{\\([A-Za-z]+)\}\{([^{}]*)\}", s):
        if kind != "provide" or name not in defs:
            defs[name] = val
    return defs

def expand(path, defs):
    for _ in range(10):
        new = re.sub(r"\\([A-Za-z]+)\s*", lambda m: defs.get(m.group(1), m.group(0)), path)
        if new == path:
            break
        path = new
    return path

def resolve(path, defs=None):
    path = expand(path, defs or {"figdir": FIGDIR}).replace(" ", "")
    full = os.path.normpath(os.path.join(paper, path))
    if not os.path.splitext(full)[1]:
        full += ".tex"
    return full

def strip_comments(s):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "%", ln) for ln in s.splitlines())

# \IfFileExists{file}{yes}{no} is decided now, against the source tree
while True:
    m = re.search(r"\\IfFileExists\{", text)
    if not m:
        break
    a = arg_end(text, m.end() - 1)
    b = arg_end(text, a)
    c = arg_end(text, b)
    fname = text[m.end():a - 1]
    exists = os.path.isfile(resolve(fname))
    text = text[:m.start()] + (text[a + 1:b - 1] if exists else text[b + 1:c - 1]) + text[c:]

# remaining \input{...} (macro paths, or files inside the branches resolved above)
for _ in range(10):
    m = re.search(r"\\input\{([^}]*)\}", text)
    if not m:
        break
    f = resolve(m.group(1), path_macros(text[:m.start()]))
    if not os.path.isfile(f):
        raise SystemExit(f"make_submission: cannot inline {m.group(1)} ({f})")
    # a file ends a line, so the inlined body does too (its last line may end in a comment)
    body = strip_comments(open(f).read()).rstrip("\n") + "\n"
    text = text[:m.start()] + body + text[m.end():]
else:
    raise SystemExit("make_submission: \\input nesting too deep")

# figures: every graphics file the build read, copied under figures/ with paths rewritten
fls = open(os.path.join(paper, "main.fls")).read()
figs = sorted({ln.split(" ", 1)[1] for ln in fls.splitlines()
               if ln.startswith("INPUT ") and ln.lower().endswith((".pdf", ".png", ".jpg", ".jpeg", ".eps"))
               and os.path.normpath(os.path.join(paper, ln.split(" ", 1)[1])).startswith(os.path.dirname(paper) + "/figures/")})
for f in figs:
    src = os.path.normpath(os.path.join(paper, f))
    rel = os.path.relpath(src, os.path.join(os.path.dirname(paper), "figures"))
    dst = os.path.join(out, "figures", rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
text = text.replace(FIGDIR, "figures/")
if "../" in text:
    bad = sorted(set(re.findall(r"\.\./[^\s}]*", text)))
    raise SystemExit(f"make_submission: relative paths left: {bad}")

open(os.path.join(out, "main.tex"), "w").write(text)
print(f"main.tex written ({len(text.splitlines())} lines), {len(figs)} figure files")
PY

cp "$PAPER/llncs/llncs.cls" "$PAPER/llncs/splncs04.bst" "$OUT/"

# 4. compile a copy of the folder on its own
TMP="$(mktemp -d)"
cp -R "$OUT"/. "$TMP"/
if (cd "$TMP" && env -u TEXINPUTS -u BSTINPUTS latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null 2>&1); then
  ERRS="$(grep -a -c -E '^! |^[^ ]+:[0-9]+: ' "$TMP/main.log" || true)"
  PAGES="$(pdfinfo "$TMP/main.pdf" 2>/dev/null | awk '/^Pages:/{print $2}')"
  UNDEF="$(grep -a -c 'undefined' "$TMP/main.log" || true)"
  echo "submission: standalone compile OK in $TMP ($ERRS errors, $PAGES pages, $UNDEF 'undefined' warnings)"
else
  echo "submission: standalone compile FAILED; log: $TMP/main.log"
  grep -a -A3 -E '^! |^[^ ]+:[0-9]+: ' "$TMP/main.log" | head -20
  exit 1
fi

# 5. remaining \pending items (the definition line excluded)
N="$(grep -o '\\pending{' "$OUT/main.tex" | wc -l | tr -d ' ')"
echo "submission: $N \\pending occurrences in paper/submission/main.tex"
