#!/usr/bin/env python3
"""Write paper/tables/table1_params.tex from data/params/model.yaml and data/derived/rev_A15.json.

Table 1 (tab:params): Symbol | Meaning | Value | Source, in three blocks (agents; forces; numerics and
criteria), LNCS width 12.2 cm. Model values are read from model.yaml; the thresholds and horizons of the numerics
block are written here and checked against the audited rows of rev_A15.json, so the table cannot drift from the code.
Quantities stated in Sect. 3 (n, w, g, R, r_c, clip bounds, density floor, tau_orca, TTC cutoff, ORCA speed limit and gate, speed cap)
are not repeated in the table.
"""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
P = yaml.safe_load((ROOT / "data" / "params" / "model.yaml").read_text())
par, model = P["parameters"], P["modes"]["corrected_forward"]
A15 = {r["id"]: r["value"] for r in json.loads((ROOT / "data" / "derived" / "rev_A15.json").read_text())["rows"]}


def val(key, sub=None):
    v = par[key]["value"]
    return v if sub is None else v[sub]


def g(x):
    """Plain decimal or scientific notation in LaTeX math."""
    if isinstance(x, float) and (abs(x) >= 1e4 or (0 < abs(x) < 1e-2)):
        m, e = f"{x:.1e}".split("e")
        m = m.rstrip("0").rstrip(".")
        return rf"{m}\times10^{{{int(e)}}}" if m != "1" else rf"10^{{{int(e)}}}"
    return f"{x:g}"


U = r"\,"  # thin space between number and unit
v0, r, tau = val("v0"), val("radius"), val("tau")
ez, clip = val("edge_zone"), val("speed_factor_clip")
dl = val("deadlock_criterion")
c = {k: rf"\cite{{{k}}}" for k in ("helbing2000nature", "weidmann1993", "karamouzas2014", "vandenberg2011",
                                   "vandenberg2011rvo2")}
TW = "--"

# variant wall ranges (Sect. 5.1 runs) and criteria of the numerics block (audited in C_REPORT A15)
B_W_VARIANTS, B_W_EDGE = (0.04, 0.02), 0.04
QUENCH_T, STOP_V, STOP_HOLD, RUN_T, REPLAY_DX, STALL = 120, 1e-3, 10, 600, 1e-9, 10
ESC_X, ESC_T, ESC_T_LONG = 10, 300, 900
assert A15["H1"] == f"{QUENCH_T} s" and A15["H6"] == f"{RUN_T} s cap"
assert A15["D2"].startswith(r"all active $|\mathbf v|<10^{-3}$ m/s for 10 s")
assert A15["D1"].startswith(rf"all active $|\mathbf v|<{g(dl['v_thr'])}$ m/s for {g(dl['hold'])} s")
assert A15["V8"].startswith(r"$10^{-9}$ m Gaussian per coordinate, 5 replays")
assert A15["D4"].startswith(rf"interval $\ge{STALL}$ s between exits")
assert A15["V3"].startswith(rf"blocker centre crosses $x\ge{ESC_X}$ m")
assert A15["H9"] == f"{ESC_T} s at $\\beta=1.5$, 2.5; {ESC_T_LONG} s at 3.5"
assert A15["H10"].startswith(f"{ESC_T} s; {ESC_T_LONG} s for per-step noise at $\\Delta t=0.02$ s")
assert A15["M5"] == f"$R={g(val('neighbor_radius'))}$ m"
assert A15["M2"].startswith(r"$|\Delta\mathbf v|\ge10^{-4}$ m/s") and val("ttc_min_dv2") == 1e-8
assert (val("orca_gate", "rho0"), val("orca_gate", "k")) == (4.0, 2.0)
assert model["w2_numerics"] == "fixed" and model["w2_crush"] == "off"
assert model["w2_wall_corner"] == "convex_union" and model["spawn"] == "rejection"

blocks = [
    ("Agents", [
        (r"$m$, $\tau$", r"mass; relaxation time", rf"${g(val('mass'))}${U}kg; $U({g(tau['low'])},{g(tau['high'])})${U}s",
         c["helbing2000nature"]),
        ("$v_0$", "desired speed", rf"$\mathcal N({g(v0['mean'])},{g(v0['std'])})${U}m/s, "
         rf"$\ge{g(v0['min'])}${U}m/s", c["weidmann1993"]),
        ("$r$", "radius", rf"$\mathcal N({g(r['mean'])},{g(r['std'])})${U}m, $\ge{g(r['min'])}${U}m", TW),
    ]),
    ("Forces", [
        (r"$\gamma$, $\rho_{\max}$", "speed--density relation",
         rf"${g(val('weidmann_gamma'))}${U}m$^{{-2}}$, ${g(val('weidmann_rho_max'))}${U}m$^{{-2}}$", c["weidmann1993"]),
        (r"$A$, $B$; $k$, $\kappa$", "social; contact",
         rf"${g(val('A'))}${U}N, ${g(val('B'))}${U}m; ${g(val('k'))}${U}kg/s$^2$, ${g(val('kappa'))}${U}kg/(m\,s)",
         c["helbing2000nature"]),
        ("$A_w$, $B_w$", "wall force", rf"$A$, $B$ (variants ${'$, $'.join(g(b) for b in B_W_VARIANTS)}${U}m)",
         c["helbing2000nature"]),
        (r"$B_{w,\rm edge}$; $r_c$", "jamb range; corner radius (variants)",
         rf"${g(B_W_EDGE)}${U}m; ${g(val('edge_radius'))}${U}m", TW),
        (r"$R$; clip", r"neighbour radius; bounds of $v_{\rm eff}/v_0$",
         rf"${g(val('neighbor_radius'))}${U}m; $[{g(val('speed_factor_clip')[0])},{g(val('speed_factor_clip')[1])}]$", TW),
        (r"$k_{\rm ttc}$, $\tau_0$, $\tau_{\max}$", "TTC scale; times",
         rf"${g(val('k_ttc'))}${U}N\,s$^2$, ${g(val('tau_0'))}${U}s, ${g(val('tau_max'))}${U}s", c["karamouzas2014"]),
        (r"$\tau_h$", "ORCA time horizon", rf"${g(val('time_horizon'))}${U}s", c["vandenberg2011"]),
    ]),
    ("Numerics and criteria", [
        (r"$\Delta t$; $\sigma$", "time step; noise SD", rf"${g(val('dt'))}${U}s; set per experiment", TW),
        ("", "deadlock: all speeds", rf"$<{g(dl['v_thr'])}${U}m/s for ${g(dl['hold'])}${U}s", TW),
        ("", "horizon: quench; run", rf"${QUENCH_T}${U}s; ${RUN_T}${U}s", TW),
        ("", "quench stop: all speeds", rf"$<{g(STOP_V)}${U}m/s for ${STOP_HOLD}${U}s", TW),
        ("", "replay shift (SD)", rf"${g(REPLAY_DX)}${U}m per coordinate", TW),
        ("", r"blocker escape; censoring",
         rf"$x\ge{ESC_X}${U}m; ${ESC_T}${U}s (${ESC_T_LONG}${U}s at $\beta=3.5$, per-step noise at "
         rf"$\Delta t=0.02${U}s)", TW),
        ("", "stall", rf"$\ge{STALL}${U}s between exits", TW),
    ]),
]
L = ["% generated by experiments/tables/make_table1.py from data/params/model.yaml and data/derived/rev_A15.json;"
     " do not edit",
     "\\begin{table}[t]",
     "\\caption{Model parameters and criteria. $\\mathcal N(\\mu,\\sigma)$: mean and standard deviation, clipped "
     "below; $U(a,b)$: uniform on $[a,b]$; --: this work.}",
     "\\label{tab:params}",
     "\\centering\\scriptsize\\setlength{\\tabcolsep}{3pt}",
     "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{1.85cm}>{\\raggedright\\arraybackslash}p{3.3cm}"
     ">{\\raggedright\\arraybackslash}p{5.6cm}>{\\raggedright\\arraybackslash}p{0.8cm}@{}}",
     "\\toprule",
     "Symbol & Meaning & Value & Source \\\\"]
for title, rows in blocks:
    L += ["\\midrule", f"\\multicolumn{{4}}{{@{{}}l}}{{\\emph{{{title}}}}} \\\\"]
    L += [" & ".join(row) + " \\\\" for row in rows]
L += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
out = ROOT / "paper" / "tables" / "table1_params.tex"
out.write_text("\n".join(L) + "\n")
print(f"wrote {out}")
