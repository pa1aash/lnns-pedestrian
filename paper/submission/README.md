# Single-file submission folder

Built by `make submission` (tools/make_submission.sh); everything here except this README is a build product and is not tracked.

- `main.tex`: the whole paper in one file. Every `\input` (sections, numbers.tex, tables, the Fig. 1 overlay and caption) and the compiled bibliography (from main.bbl) are inlined.
- `figures/`: every figure file the build reads, with the paths in main.tex rewritten to match.
- `llncs.cls`, `splncs04.bst`: the unmodified Springer files from paper/llncs/.

The folder compiles on its own (`latexmk -pdf main.tex`); the build script checks this in a temporary copy and reports any remaining `\pending` items. Edit the section files under paper/sections/, never this folder.
