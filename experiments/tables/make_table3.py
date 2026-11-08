#!/usr/bin/env python3
r"""Write paper/tables/table3_matched.tex from data/derived/E2_analysis.json (and E3, E4, E6, E7b).

Table 3: matched-control results. Only rows whose data exist are written: the lone-trap rows come from E2
(experiments/E2/analyze.py); the signature rows from E3 (experiments/E3/analyze.py, Delta-t signature) and E4
(experiments/E4/analyze.py, escape statistics per condition); the matched-completion rows from E6
(experiments/E6/analyze.py). The pair-class block (E7b, session 5A, data/derived/E7b_analysis.json) is printed
as a \pending line until that file exists; rerun this script once it does.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E2 = json.loads((ROOT / "data" / "derived" / "E2_analysis.json").read_text())
E3 = json.loads((ROOT / "data" / "derived" / "E3_analysis.json").read_text())
E4 = json.loads((ROOT / "data" / "derived" / "E4_analysis.json").read_text())
E6P = ROOT / "data" / "derived" / "E6_analysis.json"
E6 = json.loads(E6P.read_text()) if E6P.exists() else None
E7B = ROOT / "data" / "derived" / "E7b_analysis.json"
OUT = ROOT / "paper" / "tables" / "table3_matched.tex"
LK, ST, PL = "lone_keystone", "lone_keystone_second_trap", "pooled"
R, D, P, F = (E2["a_rates_time_to_free"], E2["d_orca_decomposition"], E2["b_replay_determinism"],
              E2["f_noise_vs_C3"])


def frac(g, a):
    c = R[g][a]
    return f"{c['freed']}/{c['n']}"


def med(a):
    m = R[PL][a]["time_to_free_km"]["median"]
    return "---" if m is None else f"{m:.1f}"


def pval(p):
    return r"$<10^{-3}$" if p < 1e-3 else f"{p:.2g}"


def vs_c3(a):
    if a == "C3_rvo2":
        return "reference"
    if a.startswith("noise"):
        return rf"$\Delta={F[PL][a]['paired_rate_diff_noise_minus_C3']:+.2f}$"
    c = D[PL][f"{a}_vs_C3_rvo2"]
    return f"{c['discordant_first_only']}:{c['discordant_second_only']}, $p={pval(c['mcnemar_exact_p'])}$"


def replay(a):
    if a.startswith("noise"):
        c = P[PL][a]
        return f"{c['seeds_disagree_on_freed']}/{c['snapshots']}"
    c = P[PL][a]
    return f"{c['freed_disagree']}/{c['replays']}"



ROWS = [
    # (label, class, arm)
    ("C3 RVO2 (target)", "---", "C3_rvo2"),
    ("C3 published", "---", "C3_pub"),
    ("drive only", "L", "drive_only"),
    ("frozen mean $+$", "L", "frozen_plus"),
    (r"noise $\sigma=0.03$", "T", "noise0p03"),
    (r"noise $\sigma=0.05$", "T", "noise0p05"),
    (r"noise $\sigma=0.07$", "T", "noise0p07"),
]


def bias_row():
    lk = sorted({R[LK][f"bias{b}"]["freed"] for b in ("0p05", "0p1", "0p2", "0p5")})
    st = [R[ST][f"bias{b}"]["freed"] for b in ("0p05", "0p1", "0p2", "0p5")]
    n_lk, n_st = R[LK]["bias0p05"]["n"], R[ST]["bias0p05"]["n"]
    lk_s = f"{lk[0]}/{n_lk}" if len(lk) == 1 else f"{lk[0]}--{lk[-1]}/{n_lk}"
    rep = sum(P[PL][f"bias{b}"]["freed_disagree"] for b in ("0p05", "0p1", "0p2", "0p5"))
    nrep = sum(P[PL][f"bias{b}"]["replays"] for b in ("0p05", "0p1", "0p2", "0p5"))
    return (r"bias $b=0.05$--$0.5$", "D (neg.)", lk_s, f"{min(st)}--{max(st)}/{n_st}",
            "---", "---", f"{rep}/{nrep}", "---")


def ci(v, lo, hi, f="{:.2f}"):
    return f"{f.format(v)} [{f.format(lo)}, {f.format(hi)}]"


def signature_rows():
    """E3 and E4 rows: free text across the six result columns."""
    h = E3["headline"]
    rows = [
        (r"noise, per step", "T",
         rf"$\ell$ = {h['ell_ps_b1p5_obs']:.2f} (pred.\ {h['ell_ps_b1p5_pred']:.2f}) at $\beta_{{\rm ref}}=1.5$, "
         rf"{h['ell_ps_b2p5_obs']:.2f} ({h['ell_ps_b2p5_pred']:.2f}) at 2.5; slope "
         + ci(h["slope_origin"], h["slope_origin_lo"], h["slope_origin_hi"])),
        (r"noise, $\sqrt{\Delta t}$-scaled", "T",
         r"$\ell$ = " + ci(h["ell_ds_obs"], h["ell_ds_lo"], h["ell_ds_hi"]) + f" (pred.\\ {h['ell_ds_pred']:.2f})"),
        ("C3 RVO2", "---",
         rf"$\ln t(0.02)/t(0.005)$ = {h['c3_ln_ratio']:.3f} (max $|\cdot|$ {h['c3_ln_ratio_maxabs']:.3f}), "
         rf"{h['c3_n_freed']}/{h['c3_n_freed'] + h['c3_n_held']} freed"),
    ]
    pc = E4["per_condition"]
    name = {"full": "noise, all mobile", "frozen": "noise, frozen neighbours", "alone": "noise, alone"}
    for c in ("full", "frozen", "alone"):
        p = pc[c]
        w = p["weibull"]
        rows.append((name[c], "T",
                     f"Arrhenius ratio {p['ratio_median']:.2f} (CI covers 1 in {p['ratio_ci_covers_1']}/{p['n_arrhenius_fits']}); "
                     + "Weibull $k$ = " + ci(w["k"], w["ci95"][0], w["ci95"][1]) + f"; {p['events']} escapes"))
    return rows


def e6_rows():
    """E6: matched completion of whole runs; free text across the six result columns (signs set in math)."""
    c, i, t, fs, lt = E6["completion"], E6["identity"], E6["time"], E6["failure_state"], E6["lifetimes"]

    def comp(a):
        x = c[a]
        return f"{x['k']}/{x['n']} [{x['wilson95'][0]:.2f}, {x['wilson95'][1]:.2f}]"

    def cls(a):
        k = fs[a]["class_counts"]
        return f"{k['lone_keystone']}/{k['lone_keystone_second_trap']}/{k['collective']}"

    def sg(x):
        return f"${x:+.2f}$"
    d = c["diff_sigma_minus_C3"]
    a3 = fs["C3_rvo2"]
    nb = t["paired_both_complete_n"]
    faster = nb - round(t["paired_frac_C3_faster"] * nb)
    return [
        ("C3 RVO2 (target)", "---",
         rf"completed {comp('C3_rvo2')}; KM median {t['km_C3_rvo2']['median']:.0f}\,s; failures "
         rf"{a3['stationary_deadlock']} at rest and {a3['moving_at_600s']} still moving at 600\,s; classes {cls('C3_rvo2')}"),
        (r"noise $\sigma^\ast$", "T",
         rf"completed {comp('C1_sigma')}, $\Delta$ = {sg(d['diff'])} [{sg(d['ci95'][0])}, {sg(d['ci95'][1])}]; "
         rf"failures {i['C3_only_fail']}:{i['sigma_only_fail']}, {pmath(i['mcnemar_exact_p'])}, "
         rf"$J={i['jaccard']:.2f}$ [{i['jaccard_ci95'][0]:.2f}, {i['jaccard_ci95'][1]:.2f}] (independent {i['jaccard_independent_mean']:.2f}); "
         rf"KM median {t['km_C1_sigma']['median']:.0f}\,s, faster than C3 RVO2 on {faster}/{nb} "
         rf"seeds where both complete; classes {cls('C1_sigma')}; stall lifetimes Weibull $k={lt['weibull']['k']:.2f}$"),
    ]


def pmath(p):
    """p in math: plain decimal for p >= 0.01, scientific below."""
    if p >= 0.01:
        return f"$p={p:.2f}$"
    m, e = f"{p:.1e}".split("e")
    return rf"$p={m}\times10^{{{int(e)}}}$"


def pair_rows():
    """E7b (session 5A): quench arms on the pair library; free text, from E7b_analysis.json only."""
    E = json.loads(E7B.read_text())
    q, n = E["b_quench"], E["n_snapshots"]

    def f(a):
        return f"{q[a]['freed']}/{q[a]['n']}" if a in q else None

    def km_(a):
        m = q.get(a, {}).get("km_median_s")
        return f", $t_{{1/2}}$ = {m:.1f}\\,s" if m is not None else ""
    rows = []
    pv = E.get("c_decomposition", {}).get("pub_vs_rvo2")
    rows.append(("C3 RVO2 (target)", "---", f"freed {f('C3_rvo2')}; replays identical "
                 f"({q['C3_rvo2']['replays'] - q['C3_rvo2']['replay_discordant_snapshots']}/{q['C3_rvo2']['replays']})"))
    if pv:
        rows.append(("C3 published", "N", f"freed {f('C3_pub')}; vs C3 RVO2 {pv['disc_a_only']}:{pv['disc_b_only']}, "
                     + pmath(pv['mcnemar_p'])))
    rows.append(("ORCA parts", "L", f"drive only {f('drive_only')}{km_('drive_only')}; constraint only "
                 f"{f('constraint_only_rvo2')} (RVO2), {f('constraint_only_pub')} (published); frozen mean $+$ "
                 f"{f('frozen_plus')}, $-$ {f('frozen_minus')}"))
    bs = [k for k in q if k.startswith("bias") and not k.startswith("biasm")]
    bm = [k for k in q if k.startswith("biasm")]
    if bs:
        h = E.get("b_handedness", {}).get("pooled", {})
        fp = E["a_statics"].get("fold_prediction", {})
        txt = (f"$+b$ = 0.01--0.1: freed {q[bs[0]]['freed']}--{q[bs[-1]]['freed']}/{n}; $-b$: "
               f"{', '.join(str(q[k]['freed']) for k in bm)}/{n}")
        if h:
            txt += f"; favoured member first in {h['favoured_first']}/{h['freed']}"
        if fp:
            txt += f"; static fold predicts {fp['agree']}/{fp['n']} outcomes"
        rows.append(("lateral bias $\\pm b$", "D", txt))
    ns = [k for k in q if k.startswith("noise")]
    if ns:
        rows.append(("noise $\\sigma$ = 0.01--0.05", "T", ", ".join(f"{q[k]['freed']}/{q[k]['n']}" for k in ns)
                     + " runs freed" + km_(ns[0]).replace("$t_{1/2}$", "$t_{1/2}(0.01)$")))
    ds = [k for k in q if k.startswith("delta")]
    if ds:
        rows.append(("displacement $+\\delta$", "D", "$\\delta$ = 1, 10, 30\\,mm: freed "
                     + ", ".join(f"{q[k]['freed']}" for k in ds) + f"/{n}"))
    mb = E.get("s3_matched")
    if not mb:
        rows.append(("matched bias $b^\\ast$", "D", r"\pending{fit of $b^\ast$ to C3 on rate and its held-out signatures (E7b, S9g)}"))
    else:
        for key, name in (("rvo2", "C3 RVO2"), ("pub", "C3 published")):
            m = mb.get(key)
            if not m:
                continue
            r, j, h = m["rate"], m["jaccard_unresolved"], m["handedness"]
            rows.append((f"$b^\\ast$ = {m['b_star']:.3f} (to {name})", "D",
                         f"freed {r['freed_a']}/{n} vs {r['freed_b']}/{n}, {r['disc_a_only']}:{r['disc_b_only']}, "
                         + pmath(r["mcnemar_p"]) + f"; $J$ = {j['value']:.2f} [{j['ci95'][0]:.2f}, {j['ci95'][1]:.2f}]; "
                         f"favoured member first {h['plus_lower_first']}/{h['plus_n']} ($+b^\\ast$), "
                         f"{h['minus_upper_first']}/{h['minus_n']} ($-b^\\ast$)"))
    return rows


def main():
    lines = [
        "% generated by experiments/tables/make_table3.py from data/derived/E2_analysis.json, E3_analysis.json, E4_analysis.json and E6_analysis.json; do not edit",
        r"\begin{table}[p]",
        r"\caption{Matched-control results. Lone trap: blocker freed within 120\,s from 60 corrected-forward "
        r"deadlock snapshots (Lone: 34 lone keystone; Second: 26 with a second trap), paired against C3 RVO2 by snapshot. Noise rows "
        r"count runs (5 seeds per snapshot) and C1 + noise is abbreviated noise; vs C3 RVO2 gives discordant counts with "
        r"the exact McNemar $p$, or the paired rate difference $\Delta$ for noise; $t_{1/2}$ is the Kaplan--Meier median "
        r"time-to-free; Replay counts $10^{-9}$\,m replays that differ from the unperturbed run, or for noise the "
        r"snapshots whose seeds disagree; $J$ is the Jaccard "
        r"overlap of the snapshots left unresolved with those C3 RVO2 leaves unresolved. Signature rows: "
        r"$\ell=\ln\hat\lambda(0.005)/\hat\lambda(0.02)$ against the Arrhenius prediction with the exact discrete "
        r"$k_BT_{\rm eff}$ (mean over 20 snapshots; slope of observed on predicted through the origin, 95\% CI); the "
        r"Arrhenius ratio is the fitted slope of $\ln\hat\lambda$ against $1/k_BT_{\rm eff}$ over $-\Delta U_{\rm cond}$ "
        r"(median over snapshots), and $k$ the pooled Weibull shape. Whole runs: completion within 600\,s with Wilson "
        r"intervals; $\Delta$ is the paired difference from C3 RVO2 (Newcombe interval); failures gives the seeds that fail "
        r"in one arm only (C3 RVO2 : noise) with the exact McNemar $p$; $J$ is the Jaccard overlap of the failing seeds, with its "
        r"expectation for independent failures; KM is the Kaplan--Meier median completion time; classes count the "
        r"rebuilt final states as lone keystone / with a second trap / collective; stalls are intervals of at least "
        r"10\,s without an exit.}",
        r"\label{tab:matched}",
        r"\centering\scriptsize\setlength{\tabcolsep}{2.5pt}",
        r"\begin{tabular}{@{}llcclrlc@{}}",
        r"\toprule",
        r"Control & Class & Lone & Second & vs C3 RVO2 & $t_{1/2}$ (s) & Replay & $J$ \\",
        r"\midrule",
    ]
    for label, cls, a in ROWS:
        j = f"{F[PL][a]['jaccard']:.2f}" if a.startswith("noise") else "---"
        lines.append(f"{label} & {cls} & {frac(LK, a)} & {frac(ST, a)} & {vs_c3(a)} & {med(a)} & {replay(a)} & {j} \\\\")
    lines.append(" & ".join(bias_row()) + r" \\")
    lines += [r"\midrule", r"\multicolumn{8}{@{}l}{\emph{Signature tests: $\Delta t$ scaling (E3) and escape statistics (E4)}} \\"]
    for label, cls, text in signature_rows():
        text = re.sub(r"(?<![\w$])-(\d)", r"$-$\1", text)
        lines.append(f"{label} & {cls} & \\multicolumn{{6}}{{>{{\\raggedright\\arraybackslash}}p{{7.7cm}}}}{{{text}}} \\\\")
    if E6 is not None:
        lines += [r"\midrule", r"\multicolumn{8}{@{}l}{\emph{Matched completion of whole runs (E6): "
                  rf"{E6['n']} seeds, $w=0.8$\,m, 600\,s, $\sigma^\ast={E6['sigma_star']}$\,m/s}}}} \\"]
        for label, cls, text in e6_rows():
            lines.append(f"{label} & {cls} & \\multicolumn{{6}}{{>{{\\raggedright\\arraybackslash}}p{{7.7cm}}}}{{{text}}} \\\\")
    lines += [r"\midrule"]
    lines += [r"\multicolumn{8}{@{}l}{\emph{Pair class (E7b): 46 corrected-forward pair snapshots ($B_w=0.04$), freed within 120\,s}} \\"]
    if E7B.exists():
        for label, cls, text in pair_rows():
            lines.append(f"{label} & {cls} & \\multicolumn{{6}}{{>{{\\raggedright\\arraybackslash}}p{{7.7cm}}}}{{{text}}} \\\\")
    else:
        lines += [r"\multicolumn{8}{@{}l}{\pending{pair-class rows await data/derived/E7b\_analysis.json}} \\"]
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT} ({len(ROWS) + 1 + len(signature_rows())} rows)")


if __name__ == "__main__":
    main()
