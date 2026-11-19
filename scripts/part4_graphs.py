"""Part 4: memory hierarchy graphs and tables.

Required graphs: (i) dl1 miss rate and IPC vs L1 capacity, (ii) dl1 miss rate
and IPC vs block size, (iii) CPI vs memory latency with and without L2.
Extra: 3C miss breakdown (question a) and L1 misses that reach memory (d).
"""
import os

import numpy as np
import matplotlib.pyplot as plt

from plotlib import (BENCHES, COLORS, MARKERS, DATA, RES, load, line_graph,
                     bench_lines, grouped_bars, write_csv)

SIZES = [1, 4, 16, 64]            # KB
BLOCKS = [8, 16, 32, 64]          # bytes
LATS = [25, 50, 100, 200]         # cycles

cap = {(b, k): load(b, f"P4a_dl1_{k}KB") for b in BENCHES for k in SIZES}
blk = {(b, k): load(b, f"P4b_blk{k}") for b in BENCHES for k in BLOCKS}
lat = {(b, k, l2): load(b, f"P4c_lat{k}_{'L2' if l2 else 'noL2'}")
       for b in BENCHES for k in LATS for l2 in (True, False)}


def row(b, part, setting, s):
    n = s["sim_num_insn"]
    return {"benchmark": b, "part": part, "setting": setting,
            "sim_num_insn": int(n), "sim_cycle": int(s["sim_cycle"]),
            "sim_IPC": s["sim_IPC"], "sim_CPI": s["sim_CPI"],
            "il1_miss_rate": s["il1.miss_rate"], "dl1_miss_rate": s["dl1.miss_rate"],
            "ul2_miss_rate": s.get("ul2.miss_rate", ""),
            "il1_misses_per_1000": round(1000 * s["il1.misses"] / n, 2),
            "dl1_misses_per_1000": round(1000 * s["dl1.misses"] / n, 2)}


rows = []
for b in BENCHES:
    rows += [row(b, "4a", f"dl1 {k}KB", cap[(b, k)]) for k in SIZES]
    rows += [row(b, "4b", f"block {k}B", blk[(b, k)]) for k in BLOCKS]
    rows += [row(b, "4c", f"mem:lat {k} {'with' if l2 else 'no'} L2", lat[(b, k, l2)])
             for l2 in (True, False) for k in LATS]
write_csv("part4_table.csv", rows)

# ---- (i) capacity
line_graph("part4_g1_dl1_miss_vs_capacity.png",
           "Part 4, Graph 1a: L1 data-cache miss rate vs capacity",
           "L1 data-cache capacity (KB) [-cache:dl1], 4-way, 32 B blocks, log2 scale",
           "dl1 miss rate (% of data accesses)", SIZES,
           bench_lines(lambda b, k: 100 * cap[(b, k)]["dl1.miss_rate"], SIZES),
           fmt="{:.2f}%", default_x=16, default_label="default (16 KB)")
line_graph("part4_g2_ipc_vs_capacity.png",
           "Part 4, Graph 1b: IPC vs L1 data-cache capacity",
           "L1 data-cache capacity (KB) [-cache:dl1], 4-way, 32 B blocks, log2 scale",
           "IPC (instructions per cycle)", SIZES,
           bench_lines(lambda b, k: cap[(b, k)]["sim_IPC"], SIZES),
           default_x=16, default_label="default (16 KB)")

# ---- (ii) block size
line_graph("part4_g3_dl1_miss_vs_block.png",
           "Part 4, Graph 2a: L1 data-cache miss rate vs block size",
           "L1 data-cache block size (bytes) [-cache:dl1], 16 KB, 4-way, log2 scale",
           "dl1 miss rate (% of data accesses)", BLOCKS,
           bench_lines(lambda b, k: 100 * blk[(b, k)]["dl1.miss_rate"], BLOCKS),
           fmt="{:.2f}%", default_x=32, default_label="default (32 B)")
line_graph("part4_g4_ipc_vs_block.png",
           "Part 4, Graph 2b: IPC vs L1 data-cache block size",
           "L1 data-cache block size (bytes) [-cache:dl1], 16 KB, 4-way, log2 scale",
           "IPC (instructions per cycle)", BLOCKS,
           bench_lines(lambda b, k: blk[(b, k)]["sim_IPC"], BLOCKS),
           fmt="{:.4f}", default_x=32, default_label="default (32 B)")

# ---- (iii) memory latency
series = []
for b in BENCHES:
    for l2 in (True, False):
        series.append((f"{b} ({'with L2' if l2 else 'no L2'})",
                       [lat[(b, k, l2)]["sim_CPI"] for k in LATS],
                       COLORS[b], MARKERS[b], "-" if l2 else (0, (4, 2)), not l2))
line_graph("part4_g5_cpi_vs_latency.png",
           "Part 4, Graph 3: CPI vs main-memory latency, with and without L2",
           "Main-memory latency, first chunk (cycles) [-mem:lat <lat> 2]",
           "CPI (cycles per instruction), log scale", LATS, series, log2x=False,
           logy=True)

# CPI cost of each extra 100 cycles of memory latency (least-squares slope)
slopes = []
for b in BENCHES:
    for l2 in (True, False):
        ys = [lat[(b, k, l2)]["sim_CPI"] for k in LATS]
        slope = np.polyfit(LATS, ys, 1)[0] * 100
        slopes.append({"benchmark": b, "L2": "with L2" if l2 else "no L2",
                       "CPI_at_25": ys[0], "CPI_at_200": ys[-1],
                       "CPI_per_100_cycles": round(slope, 4)})
write_csv("part4c_slopes.csv", slopes)

# ---- (d) which L1 misses go to memory when L2 is removed
mpki = {b: [1000 * lat[(b, 200, True)][k] / lat[(b, 200, True)]["sim_num_insn"]
            for k in ("il1.misses", "dl1.misses")] for b in BENCHES}
grouped_bars("part4_g7_l1_misses_per_1000.png",
             "Part 4, Graph 5: L1 misses per 1000 instructions (default L1 caches)",
             "Cache", "Misses per 1000 instructions",
             ["L1 instruction cache (il1)", "L1 data cache (dl1)"], mpki, fmt="{:.1f}")

# ---- (a) 3C breakdown, if the extra runs exist (scripts/run_P4_3c.sh)
def finished(path):
    return os.path.exists(path) and "sim_IPC" in open(path).read()


have3c = all(finished(f"{RES}/{b}_P4x_dl1_{t}.txt") for b in BENCHES
             for t in ["4MB"] + [f"{k}KB_full" for k in SIZES])
if have3c:
    c3 = []
    for b in BENCHES:
        huge = load(b, "P4x_dl1_4MB")
        for k in SIZES:
            real = cap[(b, k)]
            full = load(b, f"P4x_dl1_{k}KB_full")
            acc = real["dl1.accesses"]
            comp = huge["dl1.misses"]
            capm = max(full["dl1.misses"] - comp, 0)
            conf = real["dl1.misses"] - full["dl1.misses"]
            c3.append({"benchmark": b, "dl1_KB": k, "accesses": int(acc),
                       "total_misses": int(real["dl1.misses"]),
                       "compulsory": int(comp), "capacity": int(capm),
                       "conflict": int(conf),
                       "compulsory_pct": round(100 * comp / acc, 3),
                       "capacity_pct": round(100 * capm / acc, 3),
                       "conflict_pct": round(100 * conf / acc, 3),
                       "miss_rate_pct": round(100 * real["dl1.miss_rate"], 3)})
    write_csv("part4a_3c.csv", c3)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), sharey=False)
    parts = [("compulsory_pct", "Compulsory", "#4a6b7c"),
             ("capacity_pct", "Capacity", "#e8a33d"),
             ("conflict_pct", "Conflict", "#9b59b6")]
    for ax, b in zip(axes, BENCHES):
        rs = [r for r in c3 if r["benchmark"] == b]
        bottom = np.zeros(len(rs))
        for key, label, col in parts:
            vals = np.array([max(r[key], 0) for r in rs])
            ax.bar([f"{r['dl1_KB']} KB" for r in rs], vals, bottom=bottom,
                   label=label, color=col)
            bottom += vals
        for i, r in enumerate(rs):
            ax.text(i, bottom[i], f"{r['miss_rate_pct']:.2f}%", ha="center",
                    va="bottom", fontsize=8)
        ax.set_title(b)
        ax.set_xlabel("L1 data-cache capacity [-cache:dl1], 4-way, 32 B blocks")
        ax.set_ylabel("Misses (% of data accesses)")
        ax.grid(alpha=0.3, axis="y")
        ax.legend(fontsize=9)
    fig.suptitle("Part 4, Graph 4: L1 data-cache misses split into the 3 Cs")
    plt.tight_layout()
    plt.savefig(f"{DATA}/part4_g6_3c_breakdown.png", dpi=150)
    plt.close()

# ---- terminal summary for the write-up
print("\n(a) capacity        dl1 miss%   IPC")
for b in BENCHES:
    for k in SIZES:
        s = cap[(b, k)]
        print(f"{b:<11} {k:>3} KB   {100*s['dl1.miss_rate']:>7.2f}   {s['sim_IPC']:.4f}")
print("\n(b) block size      dl1 miss%   IPC")
for b in BENCHES:
    for k in BLOCKS:
        s = blk[(b, k)]
        print(f"{b:<11} {k:>3} B    {100*s['dl1.miss_rate']:>7.2f}   {s['sim_IPC']:.4f}")
print("\n(c) CPI per extra 100 cycles of memory latency")
for r in slopes:
    print(f"{r['benchmark']:<11} {r['L2']:<8} CPI {r['CPI_at_25']:.3f} -> {r['CPI_at_200']:.3f}"
          f"   slope {r['CPI_per_100_cycles']:.3f} CPI / 100 cycles")
print("\n(d) L1 misses per 1000 instructions (default caches)")
for b in BENCHES:
    print(f"{b:<11} il1 {mpki[b][0]:.2f}   dl1 {mpki[b][1]:.2f}")
if have3c:
    print("\n(a) 3C split (% of data accesses)")
    for r in c3:
        print(f"{r['benchmark']:<11} {r['dl1_KB']:>3} KB  comp {r['compulsory_pct']:.3f}  "
              f"cap {r['capacity_pct']:.3f}  conf {r['conflict_pct']:.3f}  total {r['miss_rate_pct']:.3f}")
print("\nWrote part4 CSVs and graphs in data/")
