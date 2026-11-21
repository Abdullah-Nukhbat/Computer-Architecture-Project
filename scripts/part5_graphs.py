import re, csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = "/mnt/d/CA_Project/results"
DATA = "/mnt/d/CA_Project/data"
benches = ["compress95", "cc1"]
colors = {"compress95": "#0f8b8d", "cc1": "#d64550"}
markers = {"compress95": "o", "cc1": "s"}

preds = [  # (key, axis label, short name)
    ("perfect",   "Perfect\n-bpred perfect",                  "perfect"),
    ("nottaken",  "Static not-taken\n-bpred nottaken",        "not-taken"),
    ("bimod512",  "Bimodal 512\n-bpred bimod\n-bpred:bimod 512", "bimod 512"),
    ("bimod2048", "Bimodal 2048\n(default)\n-bpred:bimod 2048",  "bimod 2048"),
    ("2lev",      "2-level GAg\n-bpred 2lev\n-bpred:2lev 1 1024 8 0", "2lev GAg"),
    ("comb",      "Combined\n-bpred comb\n-bpred:comb 1024",  "comb"),
]
Ws = [1, 2, 4, 8]

def read(path):
    d = {}
    for line in open(path):
        m = re.match(r"^(\S+)\s+([-0-9.eE+]+)\s", line)
        if m:
            d[m.group(1)] = float(m.group(2))
    return d

def load(path):
    if not os.path.exists(path):
        raise SystemExit(f"Missing file: {path}")
    s = read(path)
    if "sim_IPC" not in s:
        raise SystemExit(f"No sim_IPC in {path}")
    return s

def bp_stats(s, key, path):
    """returns (direction hit rate, misses). Perfect has no predictor stats."""
    dk = next((k for k in s if re.match(r"^bpred_\w+\.bpred_dir_rate$", k)), None)
    mk = next((k for k in s if re.match(r"^bpred_\w+\.misses$", k)), None)
    if key == "perfect":
        return 1.0, 0.0
    if dk is None or mk is None:
        found = [k for k in s if k.startswith("bpred")]
        raise SystemExit(f"Predictor stats not found in {path}. Keys: {found}")
    return s[dk], s[mk]

S = {}
rows = []
for key, _, short in preds:
    for b in benches:
        path = f"{RES}/{b}_P5_{key}.txt"
        s = load(path)
        dr, mis = bp_stats(s, key, path)
        n = s["sim_num_insn"]
        S[(b, key)] = {"s": s, "dir": dr, "mis": mis,
                       "mpki": 1000 * mis / n,
                       "ipc": s["sim_IPC"], "cpi": s["sim_CPI"]}
for b in benches:
    perf = S[(b, "perfect")]["ipc"]
    for key, _, short in preds:
        r = S[(b, key)]; s = r["s"]; n = s["sim_num_insn"]
        r["norm"] = r["ipc"] / perf
        rows.append({
            "benchmark": b, "predictor": key,
            "sim_num_insn": int(n), "sim_cycle": int(s["sim_cycle"]),
            "sim_IPC": r["ipc"], "sim_CPI": r["cpi"],
            "ipc_normalized_to_perfect": round(r["norm"], 4),
            "ipc_loss_vs_perfect_pct": round(100 * (1 - r["norm"]), 2),
            "branches_pct": round(100 * s["sim_num_branches"] / n, 2),
            "bpred_dir_rate": round(r["dir"], 4),
            "misses": int(r["mis"]),
            "MPKI": round(r["mpki"], 2),
            "MPKI_check_from_dir_rate": round((1 - r["dir"]) * s["sim_num_branches"] / n * 1000, 2),
        })
with open(f"{DATA}/part5_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# extra runs: perfect vs the Part 2 bimodal runs at each width
X = {}
xrows = []
for b in benches:
    for W in Ws:
        perf = load(f"{RES}/{b}_P5x_W{W}_perfect.txt")["sim_IPC"]
        bim = load(f"{RES}/{b}_P2_W{W}_ooo.txt")["sim_IPC"]
        X[(b, W)] = (bim, perf, 100 * (1 - bim / perf))
        xrows.append({"benchmark": b, "W": W, "ipc_bimod2048": bim,
                      "ipc_perfect": perf, "loss_pct": round(100 * (1 - bim / perf), 2)})
with open(f"{DATA}/part5x_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(xrows[0].keys()))
    w.writeheader()
    w.writerows(xrows)

# ---------- graphs
def bar_graph(fname, title, ylabel, plist, data, fmt, ylim=None,
              hline=None, hline_label=None, note=None):
    n = len(plist); w = 0.38
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for i, b in enumerate(benches):
        xs = [j + (i - 0.5) * w for j in range(n)]
        ax.bar(xs, data[b], w, label=b, color=colors[b])
        for x, v in zip(xs, data[b]):
            ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=8)
    if hline is not None:
        ax.axhline(hline, linestyle=":", color="gray", label=hline_label)
    ax.set_xticks(range(n))
    ax.set_xticklabels([p[1] for p in plist], fontsize=8)
    ax.set_xlabel("Branch predictor (options used)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=9)
    if note:
        fig.text(0.01, 0.01, note, fontsize=8, color="gray")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.savefig(f"{DATA}/{fname}", dpi=150)
    plt.close()

real = preds[1:]
bar_graph("part5_g1_dir_rate.png",
          "Part 5, Graph 1: branch-direction prediction accuracy",
          "Direction-prediction rate (% of branches) [bpred_dir_rate]",
          preds, {b: [100 * S[(b, k)]["dir"] for k, _, _ in preds] for b in benches},
          "{:.1f}%", ylim=(0, 112),
          note="Perfect = 100% by definition (sim-outorder prints no predictor statistics for it).")

bar_graph("part5_g2_ipc_normalized.png",
          "Part 5, Graph 2: IPC normalized to the perfect predictor",
          "IPC / IPC with perfect predictor",
          preds, {b: [S[(b, k)]["norm"] for k, _, _ in preds] for b in benches},
          "{:.3f}", ylim=(0, 1.15), hline=1.0, hline_label="Perfect predictor (= 1.0)")

bar_graph("part5_g3_mpki.png",
          "Part 5, Graph 3: mispredictions per 1000 instructions (MPKI)",
          "MPKI = misses / sim_num_insn x 1000",
          real, {b: [S[(b, k)]["mpki"] for k, _, _ in real] for b in benches},
          "{:.1f}")

bar_graph("part5_g4_ipc_absolute.png",
          "Part 5, Graph 4: absolute IPC per predictor (default 4-wide machine)",
          "IPC (instructions per cycle)",
          preds, {b: [S[(b, k)]["ipc"] for k, _, _ in preds] for b in benches},
          "{:.2f}", ylim=(0, 4.2), hline=4, hline_label="Peak IPC (width 4)")

# Graph 5: CPI vs MPKI
fig, ax = plt.subplots(figsize=(8.5, 6))
slopes = {}
for b in benches:
    xs = [S[(b, k)]["mpki"] for k, _, _ in preds]
    ys = [S[(b, k)]["cpi"] for k, _, _ in preds]
    slope, icpt = np.polyfit(xs, ys, 1)
    slopes[b] = slope * 1000
    ax.scatter(xs, ys, marker=markers[b], color=colors[b], s=60, label=b, zorder=3)
    xx = np.linspace(0, max(xs) * 1.05, 50)
    ax.plot(xx, slope * xx + icpt, linestyle=":", color=colors[b],
            label=f"{b} fit: +{slope*1000:.1f} cycles per misprediction")
    for x, y, (_, _, short) in zip(xs, ys, preds):
        ax.annotate(short, (x, y), textcoords="offset points", xytext=(5, 5),
                    fontsize=8, color=colors[b])
ax.set_xlabel("Mispredictions per 1000 instructions (MPKI)")
ax.set_ylabel("CPI (cycles per instruction)")
ax.set_title("Part 5, Graph 5: CPI vs MPKI across predictors")
ax.grid(alpha=0.3)
ax.legend(fontsize=8, handlelength=3)
plt.tight_layout()
plt.savefig(f"{DATA}/part5_g5_cpi_vs_mpki.png", dpi=150)
plt.close()

# Graph 6: IPC lost to mispredictions vs width
xs = list(range(len(Ws)))
fig, ax = plt.subplots(figsize=(8.5, 6))
for b in benches:
    ys = [X[(b, W)][2] for W in Ws]
    ax.plot(xs, ys, linestyle="-", linewidth=2.2, markersize=7, marker=markers[b],
            color=colors[b], label=b)
    for x, y in zip(xs, ys):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points",
                    xytext=(0, 9 if b == "compress95" else -15), ha="center",
                    fontsize=8, color=colors[b])
ax.axvline(2, linestyle=":", color="gray", linewidth=1)
ax.text(2.03, 0.98, "default width (W=4)", transform=ax.get_xaxis_transform(),
        fontsize=8, color="gray", va="top")
ax.set_xticks(xs)
ax.set_xticklabels([str(W) for W in Ws])
ax.set_xlabel("Machine width W (instructions per cycle) [-fetch:ifqsize / -decode:width / "
              "-issue:width / -commit:width / -res:ialu]\nRUU 64, LSQ 32; bimodal 2048 vs perfect")
ax.set_ylabel("IPC lost to mispredictions (%)\n= 1 - IPC(bimodal) / IPC(perfect)")
ax.set_title("Part 5, Graph 6: cost of branch mispredictions vs machine width")
ax.grid(alpha=0.3)
ax.legend(fontsize=9, handlelength=4.5)
plt.tight_layout()
plt.savefig(f"{DATA}/part5_g6_loss_vs_width.png", dpi=150)
plt.close()

# ---------- terminal tables for the write-up
print("\nbenchmark   predictor     dir%    MPKI    IPC    IPC/perfect")
for b in benches:
    for k, _, short in preds:
        r = S[(b, k)]
        print(f"{b:<11} {short:<11} {100*r['dir']:>6.2f}  {r['mpki']:>6.2f}  {r['ipc']:.4f}   {r['norm']:.4f}")
print("\nMPKI cross-check (misses/insn vs (1-dir_rate)*branches/insn) - should be close:")
for b in benches:
    for k, _, short in preds[1:]:
        r = next(x for x in rows if x["benchmark"] == b and x["predictor"] == k)
        print(f"{b:<11} {short:<11} MPKI {r['MPKI']:>6.2f}   check {r['MPKI_check_from_dir_rate']:>6.2f}")
print("\nBranch share of instructions:")
for b in benches:
    print(f"{b:<11} {next(x for x in rows if x['benchmark']==b)['branches_pct']}%")
print("\nBest predictor per benchmark (highest IPC, excluding perfect):")
for b in benches:
    k, _, short = max(preds[1:], key=lambda p: S[(b, p[0])]["ipc"])
    r = S[(b, k)]
    print(f"{b:<11} {short}: IPC {r['ipc']:.4f}, loses {100*(1-r['norm']):.1f}% vs perfect, MPKI {r['mpki']:.2f}")
print("\nNot-taken loses vs perfect:")
for b in benches:
    print(f"{b:<11} {100*(1-S[(b,'nottaken')]['norm']):.1f}%")
print("\nImplied cost per misprediction (slope of CPI vs MPKI x 1000):")
for b in benches:
    print(f"{b:<11} about {slopes[b]:.1f} cycles per misprediction")
print("\nWidth effect (RUU 64): W  IPC(bimod)  IPC(perfect)  loss%")
for b in benches:
    for W in Ws:
        bim, perf, loss = X[(b, W)]
        print(f"{b:<11}{W:>3}   {bim:>8.3f}   {perf:>9.3f}   {loss:>6.1f}%")
print("\nConsistency: bimod 2048 run vs Part 3 RUU 16 run (same config) - should match:")
for b in benches:
    p3 = read(f"{RES}/{b}_P3_ruu16.txt")["sim_IPC"]
    print(f"{b:<11} Part 5 {S[(b,'bimod2048')]['ipc']:.4f}   Part 3 {p3:.4f}")
print("\nWrote part5_table.csv, part5x_table.csv and 6 PNG graphs in data/")