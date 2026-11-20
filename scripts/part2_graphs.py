import re, csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paths import RES, DATA  # reads .env (defaults: repo results/ and data/)
benches = ["compress95", "cc1"]
Ws = [1, 2, 4, 8]
modes = ["ooo", "inorder"]
mode_name = {"ooo": "out-of-order", "inorder": "in-order"}
colors = {"compress95": "#0f8b8d", "cc1": "#d64550"}
markers = {"compress95": "o", "cc1": "s"}
style = {"ooo": "-", "inorder": (0, (4, 2))}

def read(path):
    d = {}
    for line in open(path):
        m = re.match(r"^(\S+)\s+([-0-9.eE+]+)\s", line)
        if m:
            d[m.group(1)] = float(m.group(2))
    return d

D = {}
rows = []
for b in benches:
    for W in Ws:
        for m in modes:
            path = f"{RES}/{b}_P2_W{W}_{m}.txt"
            if not os.path.exists(path):
                raise SystemExit(f"Missing file: {path}")
            s = read(path)
            D[(b, W, m)] = s
            rows.append({
                "benchmark": b, "W": W, "mode": m,
                "sim_num_insn": int(s["sim_num_insn"]),
                "sim_cycle": int(s["sim_cycle"]),
                "sim_IPC": s["sim_IPC"],
                "sim_CPI": s["sim_CPI"],
                "ipc_pct_of_peak": round(100 * s["sim_IPC"] / W, 1),
                "ruu_occupancy": s.get("ruu_occupancy", ""),
                "ruu_full": s.get("ruu_full", ""),
                "bpred_dir_rate": s.get("bpred_bimod.bpred_dir_rate", ""),
            })

with open(f"{DATA}/part2_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

xs = list(range(len(Ws)))  # evenly spaced positions for W = 1, 2, 4, 8
XLABEL = ("Machine width W (instructions per cycle)\n"
          "[-fetch:ifqsize / -decode:width / -issue:width / -commit:width / -res:ialu]")

def line_graph(fname, title, ylabel, getter, use_modes, fmt="{:.2f}",
               hline=None, hline_label=None, peak=False, ylim=None):
    fig, ax = plt.subplots(figsize=(8.5, 6))
    for b in benches:
        for m in use_modes:
            ys = [getter(b, W, m) for W in Ws]
            label = f"{b} ({mode_name[m]})" if len(use_modes) > 1 else b
            ax.plot(xs, ys, linestyle=style[m], linewidth=2.2, markersize=7,
            marker=markers[b], color=colors[b], label=label,
            markerfacecolor=(colors[b] if m == "ooo" else "white"),
            markeredgewidth=1.8)
            off = 8 if m == "ooo" else -14
            for x, y in zip(xs, ys):
                ax.annotate(fmt.format(y), (x, y), textcoords="offset points",
                            xytext=(0, off), ha="center", fontsize=8, color=colors[b])
    if peak:
        ax.plot(xs, Ws, ":", color="gray", label="Peak IPC (= W)")
    if hline is not None:
        ax.axhline(hline, linestyle=":", color="gray", label=hline_label)
    ax.axvline(2, linestyle=":", color="gray", linewidth=1)
    ax.text(2.03, 0.98, "default width (W=4)", transform=ax.get_xaxis_transform(),
            fontsize=8, color="gray", va="top")
    ax.set_xticks(xs)
    ax.set_xticklabels([str(W) for W in Ws])
    ax.set_xlabel(XLABEL)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, handlelength=4.5, framealpha=0.95)
    plt.tight_layout()
    plt.savefig(f"{DATA}/{fname}", dpi=150)
    plt.close()

ipc = lambda b, W, m: D[(b, W, m)]["sim_IPC"]

# Graph 1 (required): IPC vs W, four lines
line_graph("part2_g1_ipc_vs_width.png",
           "Part 2, Graph 1: IPC vs machine width",
           "IPC (instructions per cycle)", ipc, modes, peak=True)

# Graph 2 (required): speedup of OoO over in-order
def speedup(b, W, m):
    return D[(b, W, "inorder")]["sim_cycle"] / D[(b, W, "ooo")]["sim_cycle"]
line_graph("part2_g2_speedup.png",
           "Part 2, Graph 2: speedup of out-of-order over in-order issue",
           "Speedup (cycles in-order / cycles out-of-order)", speedup, ["ooo"],
           hline=1.0, hline_label="No gain (speedup = 1)")

# Graph 3 (extra): how much of the peak is used
pct = lambda b, W, m: 100 * D[(b, W, m)]["sim_IPC"] / W
line_graph("part2_g3_pct_of_peak.png",
           "Part 2, Graph 3: IPC as a percentage of peak (IPC / W)",
           "IPC as % of peak width", pct, modes, fmt="{:.0f}%", ylim=(0, 110))

# Graph 4 (extra): RUU occupancy
occ = lambda b, W, m: D[(b, W, m)].get("ruu_occupancy", 0)
line_graph("part2_g4_ruu_occupancy.png",
           "Part 2, Graph 4: average RUU occupancy vs width (RUU size 64)",
           "Average RUU occupancy (entries)", occ, modes, fmt="{:.1f}",
           hline=64, hline_label="RUU size (64 entries)")

# Table printed in the terminal for your write-up
print("\nbenchmark   W   IPC(ooo)  IPC(inorder)  speedup  ooo %peak  RUUocc(ooo)")
for b in benches:
    for W in Ws:
        o = D[(b, W, "ooo")]; i = D[(b, W, "inorder")]
        print(f"{b:<11}{W:>2}   {o['sim_IPC']:>7.3f}   {i['sim_IPC']:>9.3f}   "
              f"{i['sim_cycle']/o['sim_cycle']:>7.3f}   {100*o['sim_IPC']/W:>7.1f}%   "
              f"{o.get('ruu_occupancy', float('nan')):>8.2f}")
print("\nWrote part2_table.csv and 4 PNG graphs in data/")