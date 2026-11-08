"""Shared figure helpers: style, widths, intervention colours, save and font QA."""
import subprocess
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
plt.style.use(HERE / "style.mplstyle")

CM = 1 / 2.54
FULL_W_CM = 12.2   # llncs \textwidth
HALF_W_CM = 5.9

# Okabe-Ito, one colour per intervention. Conditions within an intervention differ by line style.
ARM_COLOURS = {
    "C1": "#000000",
    "C2": "#E69F00",
    "C3 published": "#56B4E9",
    "C3 RVO2": "#0072B2",
    "C4": "#009E73",
    "noise": "#D55E00",
    "push / drive": "#CC79A7",
    "lateral bias": "#F0E442",
    "humans": "#999999",
}


def fig_full(height_cm):
    return plt.figure(figsize=(FULL_W_CM * CM, height_cm * CM), layout="constrained")


def fig_half(height_cm):
    return plt.figure(figsize=(HALF_W_CM * CM, height_cm * CM), layout="constrained")


def save(fig, name):
    """Write figures/<name>.pdf and figures/_qa/<name>.png (300 dpi)."""
    qa_dir = HERE / "_qa"
    qa_dir.mkdir(exist_ok=True)
    pdf = HERE / f"{name}.pdf"
    # 600 ppi for rasterised layers; no CreationDate, so unchanged figures rebuild byte-identically
    fig.savefig(pdf, dpi=600, metadata={"CreationDate": None})
    plt.close(fig)
    # PNG for visual QA, rendered from the PDF (the usetex Agg path needs dvipng)
    subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile",
                    str(pdf), str(qa_dir / name)], check=True)
    return pdf


def qa(name):
    """Run pdffonts on figures/<name>.pdf; return True if every font is embedded."""
    out = subprocess.run(["pdffonts", str(HERE / f"{name}.pdf")],
                         capture_output=True, text=True, check=True).stdout
    print(out)
    bad = [ln for ln in out.splitlines()[2:] if ln.split()[-5:-4] and ln.split()[-5] != "yes"]
    if bad:
        print("NOT EMBEDDED:", *bad, sep="\n")
    return not bad
