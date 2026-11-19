"""Shared helpers for the Part 4-6 graph scripts (same style as Parts 2-3)."""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

from paths import RES, DATA

BENCHES = ["compress95", "cc1"]
COLORS = {"compress95": "#0f8b8d", "cc1": "#d64550"}
MARKERS = {"compress95": "o", "cc1": "s"}


def read(path):
    """All numeric statistics of one sim-outorder output file."""
    d = {}
    for line in open(path):
        m = re.match(r"^(\S+)\s+([-0-9.eE+]+)\s", line)
        if m:
            d[m.group(1)] = float(m.group(2))
    return d


def load(bench, tag):
    path = f"{RES}/{bench}_{tag}.txt"
    if not os.path.exists(path):
        raise SystemExit(f"Missing file: {path}")
    s = read(path)
    if "sim_IPC" not in s:
        raise SystemExit(f"Run did not finish: {path}")
    return s


def line_graph(fname, title, xlabel, ylabel, xs, series, fmt="{:.2f}",
               log2x=True, default_x=None, default_label="default",
               ylim=None, xticklabels=None, logy=False):
    """series: list of (label, ys, color, marker, linestyle, hollow)."""
    fig, ax = plt.subplots(figsize=(8.5, 6))
    for i, (label, ys, color, marker, ls, hollow) in enumerate(series):
        ax.plot(xs, ys, linestyle=ls, linewidth=2.2, markersize=7, marker=marker,
                color=color, label=label, markeredgewidth=1.8,
                markerfacecolor="white" if hollow else color)
        for j, (x, y) in enumerate(zip(xs, ys)):
            # label goes below the point if another line is just above it here
            others = [sr[1][j] for k, sr in enumerate(series) if k != i]
            yall = [v for sr in series for v in sr[1]]
            if logy:
                close = any(y <= o < y * 1.35 for o in others)
            else:
                close = any(y <= o < y + 0.08 * (max(yall) - min(yall)) for o in others)
            if close and any(o == y for o in others):
                close = i % 2 == 1          # identical values: alternate
            ax.annotate(fmt.format(y), (x, y), textcoords="offset points",
                        xytext=(0, -14 if close else 8), ha="center", fontsize=8,
                        color=color)
    if log2x:
        ax.set_xscale("log", base=2)
        ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticks(xs)
    ax.set_xticklabels(xticklabels or [str(x) for x in xs])
    if default_x is not None:
        ax.axvline(default_x, linestyle=":", color="gray", linewidth=1)
        ax.text(default_x, 0.02, f" {default_label}", transform=ax.get_xaxis_transform(),
                fontsize=8, color="gray", va="bottom")
    if logy:
        from matplotlib.ticker import ScalarFormatter
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(ScalarFormatter())
        ax.yaxis.set_minor_formatter(ScalarFormatter())
        ax.tick_params(axis="y", which="minor", labelsize=7)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, handlelength=4.5, framealpha=0.95)
    plt.tight_layout()
    plt.savefig(f"{DATA}/{fname}", dpi=150)
    plt.close()


def bench_lines(getter, xs):
    """One solid line per benchmark."""
    return [(b, [getter(b, x) for x in xs], COLORS[b], MARKERS[b], "-", False)
            for b in BENCHES]


def grouped_bars(fname, title, xlabel, ylabel, groups, values, fmt="{:.2f}",
                 ylim=None, hline=None, hline_label=None, highlight=None):
    """values[bench] = list of numbers, one per group (x position)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.38
    for i, b in enumerate(BENCHES):
        xs = [j + (i - 0.5) * width for j in range(len(groups))]
        bars = ax.bar(xs, values[b], width, label=b, color=COLORS[b])
        if highlight is not None:
            bars[highlight].set_edgecolor("black")
            bars[highlight].set_linewidth(2)
        for x, v in zip(xs, values[b]):
            ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=8)
    if hline is not None:
        ax.axhline(hline, linestyle="--", color="gray", label=hline_label)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3, axis="y")
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(f"{DATA}/{fname}", dpi=150)
    plt.close()


def write_csv(fname, rows):
    import csv
    with open(f"{DATA}/{fname}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
