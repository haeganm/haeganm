#!/usr/bin/env python3
"""Redraws holdfast's partition chart in this page's colours.

    python assets/holdfast_chart.py <holdfast>/results/sweep-sync

The rows and plot calls are those of timeline() in holdfast's harness/plot.py.
Only the colours, the height, the resolution and the rounded corners change. The polls it reads
come from `python -I harness/run.py --reanalyze results/sweep-sync` in a holdfast
checkout. --narrow draws the phone-sized copy the README serves below 900 px: same
rows and calls, with the title and labels wrapped onto two lines. --original draws
holdfast's own colours and size instead, which should match its committed
docs/partition-timeline.png pixel for pixel.
"""
import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

RUN = "sync-mesh-partition-hlc-skew0-r0"
HOLDFAST = {"lines": ("#2a78d6", "#eb6834", "#1baf7a"), "surface": "#fcfcfb", "ink": "#0b0b0b",
            "ink2": "#52514e", "grid": "#e4e3de", "band": "#e4e3de"}
PAGE = {"lines": ("#a98bff", "#ff5ad9", "#5ff3ff"), "surface": "#1b1236", "ink": "#f3ebff",
        "ink2": "#b8a6e6", "grid": "#33245e", "band": "#3d2a72"}


def rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def draw(sync_dir, out, pal, size, dpi, wrap=False):
    plt.rcParams.update({
        "figure.facecolor": pal["surface"], "axes.facecolor": pal["surface"], "savefig.facecolor": pal["surface"],
        "axes.edgecolor": pal["grid"], "axes.labelcolor": pal["ink2"], "xtick.color": pal["ink2"],
        "ytick.color": pal["ink2"], "text.color": pal["ink"], "axes.grid": True, "grid.color": pal["grid"],
        "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False,
    })
    summary = {r["run_id"]: r for r in rows(sync_dir / "summary.csv")}[RUN]
    polls = rows(sync_dir / "polls" / f"{RUN}.csv")
    fig, ax = plt.subplots(figsize=size)
    cut, heal = float(summary["cut_at_ms"]) / 1000, float(summary["heal_at_ms"]) / 1000
    ax.axvspan(cut, heal, color=pal["band"], alpha=0.6, lw=0)
    ax.text((cut + heal) / 2, 0.97, "c cut off", transform=ax.get_xaxis_transform(),
            ha="center", va="top", color=pal["ink2"])
    for node, color in zip("abc", pal["lines"]):
        pts = [(int(p["t_ms"]) / 1000, float(p["lag_p95"]) / 1000) for p in polls if p["node"] == node and p["lag_p95"]]
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=2, drawstyle="steps-post", label=f"node {node}")
    end = float(summary["duration_ms"]) / 1000
    ax.axvline(end, color=pal["ink2"], lw=0.8, ls=":")
    ax.text(end, 0.97, " ingest\n stops" if wrap else " ingest stops", transform=ax.get_xaxis_transform(),
            va="top", color=pal["ink2"])
    ax.set_xlabel("seconds since the trace started")
    gap = "\n" if wrap else " "
    ax.set_ylabel(f"p95 lag behind the{gap}freshest report (s)")
    ax.set_title(f"Lag grows 1 s per second of the cut{gap}and clears 1.2 s after the heal")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out, dpi=dpi)
    plt.close(fig)


def round_corners(path, radius):
    img = Image.open(path).convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius, fill=255)
    img.putalpha(mask)
    img.save(path, optimize=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sync_dir", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--narrow", action="store_true", help="the phone-sized copy")
    ap.add_argument("--original", action="store_true", help="holdfast's own colours and size; needs --out")
    args = ap.parse_args()
    if args.original:
        if not args.out:
            ap.error("--original needs --out, so it never overwrites the page's chart")
        draw(args.sync_dir, args.out, HOLDFAST, (8, 4), 150)
    else:
        name = "holdfast-partition-narrow.png" if args.narrow else "holdfast-partition.png"
        args.out = args.out or Path(__file__).parent / name
        if args.narrow:
            draw(args.sync_dir, args.out, PAGE, (4.6, 3.9), 210, wrap=True)
        else:
            draw(args.sync_dir, args.out, PAGE, (8, 3.6), 210)
        round_corners(args.out, 24)
    print(f"wrote {args.out}")
