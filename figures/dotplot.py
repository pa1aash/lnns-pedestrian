"""Horizontal grouped dot plot: categories on the y-axis (top to bottom), one point with its interval per series.

    groups = [("baselines", [("C1", "SFM"), ("C2", "SFM+TTC")]),
              ("noise", [("noise0p03", r"$\\sigma=0.03$"), ...])]
    series = [{"values": {key: (p, lo, hi)}, "filled": True, "dy": -0.17}, ...]
    ys = dotplot(ax, groups, series)

Group headers are italic y tick labels on rows of their own; members are indented below them. A header of None
leaves a one-row gap instead. Labels are left-aligned in one column ending at the axis. Keys in a series that are
not in groups are skipped. Returns {key: y} for the rows drawn.
"""
from matplotlib.transforms import ScaledTranslation

INDENT_PT = 6.0


def dotplot(ax, groups, series, *, colour="black", ms=3.4, lw=0.8, xlim=(-0.03, 1.03)):
    ys, ticks, labels, indent = {}, [], [], []
    y = 0.0
    for header, members in groups:
        if header is not None:
            ticks.append(y)
            labels.append(r"\textit{" + header + "}")
            indent.append(False)
        y += 1.0
        for key, label in members:
            ys[key] = y
            ticks.append(y)
            labels.append(label)
            indent.append(header is not None)
            y += 1.0
    for s in series:
        dy, filled = s.get("dy", 0.0), s.get("filled", True)
        c = s.get("colour", colour)
        for key, (p, lo, hi) in s["values"].items():
            if key not in ys:
                continue
            yy = ys[key] + dy
            ax.plot([lo, hi], [yy, yy], color=c, lw=lw, solid_capstyle="butt", zorder=2)
            ax.plot([p], [yy], marker=s.get("marker", "o"), ms=ms, ls="none", zorder=3,
                    mfc=c if filled else "white", mec=c, mew=0.4 if filled else 0.8)
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels)
    ax.set_ylim(y - 0.4, -0.6)
    ax.set_xlim(*xlim)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    # left-align: pad by the widest label (indent included), then shift indented labels right
    fig = ax.figure
    tl = ax.get_yticklabels()
    for t in tl:
        t.set_horizontalalignment("left")
    r = fig.canvas.get_renderer()
    w = max(t.get_window_extent(r).width * 72 / fig.dpi + (INDENT_PT if i else 0) for t, i in zip(tl, indent))
    ax.tick_params(axis="y", pad=w + 3)
    for t, i in zip(ax.get_yticklabels(), indent):
        if i:
            t.set_transform(t.get_transform() + ScaledTranslation(INDENT_PT / 72, 0, fig.dpi_scale_trans))
    return ys
