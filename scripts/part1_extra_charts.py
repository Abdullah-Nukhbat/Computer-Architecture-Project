import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = "/mnt/d/CA_Project/data"
rows = list(csv.DictReader(open(f"{DATA}/part1_table.csv")))
colors = ["#0f8b8d", "#d64550"]

def grouped_bar(fname, title, ylabel, xlabels, keys, scale=1.0,
                fmt="{:.2f}", ylim=None, hline=None, hline_label=None):
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 5))
    for i, r in enumerate(rows):
        vals = [float(r[k]) * scale for k in keys]
        xs = [j + (i - 0.5) * width for j in range(len(keys))]
        ax.bar(xs, vals, width, label=r["benchmark"], color=colors[i])
        for x, v in zip(xs, vals):
            ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=9)
    if hline is not None:
        ax.axhline(hline, linestyle="--", color="gray", label=hline_label)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(xlabels)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(*ylim)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{DATA}/{fname}", dpi=150)
    plt.close()

grouped_bar("part1_ipc.png",
            "Part 1: IPC on the default 4-wide machine",
            "IPC (instructions per cycle)",
            ["Default configuration"], ["sim_IPC"],
            fmt="{:.2f}", ylim=(0, 4.5), hline=4,
            hline_label="Peak IPC (width 4)")

grouped_bar("part1_miss_rates.png",
            "Part 1: Cache miss rates (default configuration)",
            "Miss rate (% of references)",
            ["il1 (L1 instruction)", "dl1 (L1 data)", "ul2 (unified L2)"],
            ["il1_miss_rate", "dl1_miss_rate", "ul2_miss_rate"],
            scale=100, fmt="{:.2f}%")

grouped_bar("part1_mpki.png",
            "Part 1: Branch mispredictions (bimodal predictor)",
            "Mispredictions per 1000 instructions (MPKI)",
            ["Bimodal, 2048 entries"], ["MPKI"], fmt="{:.1f}")

print("Wrote part1_ipc.png, part1_miss_rates.png, part1_mpki.png")