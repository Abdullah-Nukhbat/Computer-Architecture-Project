import re, csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

RES = "/mnt/d/CA_Project/results"
DATA = "/mnt/d/CA_Project/data"
benches = ["compress95", "cc1"]
colors = {"compress95": "#0f8b8d", "cc1": "#d64550"}
markers = {"compress95": "o", "cc1": "s"}
caps = [1, 4, 16, 64]
blks = [8, 16, 32, 64]
lats = [25, 50, 100, 200]

def read(path):
    d = {}
    for line in open(path):
        m = re.match(r"^(\S+)\s+([-0-9.eE+]+)\s", line)
        if m:
            d[m.group(1)] = float(m.group(2))
    return d

def load(b, tag):
    p = f"{RES}/{b}_{tag}.txt"
    if not os.path.exists(p):
        raise SystemExit(f"Missing file: {p}")
    s = read(p)
    if "sim_IPC" not in s:
        raise SystemExit(f"No sim_IPC in {p}")
    return s

cap_tag = lambda K: f"P4a_dl1_{K}KB"
blk_tag = lambda B: f"P4b_blk{B}B"
lat_tag = lambda L, l2: f"P4c_lat{L}_{'L2' if l2 else 'noL2'}"
xtags = ["P4x_dl1_16KB_1way", "P4x_dl1_16KB_16way"]

# ---- load everything and write one CSV row per run
alltags = [cap_tag(K) for K in caps] + [blk_tag(B) for B in blks] + \
          [lat_tag(L, t) for L in lats for t in (True, False)] + xtags
S = {}
rows = []
for tag in alltags:
    for b in benches:
        s = load(b, tag)
        S[(b, tag)] = s
        n = s["sim_num_insn"]
        rows.append({
            "benchmark": b, "config": tag,
            "sim_num_insn": int(n), "sim_cycle": int(s["sim_cycle"]),
            "sim_IPC": s["sim_IPC"], "sim_CPI": s["sim_CPI"],
            "il1_miss_rate": s.get("il1.miss_rate", ""),
            "dl1_miss_rate": s.get("dl1.miss_rate", ""),
            "ul2_miss_rate": s.get("ul2.miss_rate", ""),
            "il1_misses_per_1000": round(1000 * s.get("il1.misses", 0) / n, 3),
            "dl1_misses_per_1000": round(1000 * s.get("dl1.misses", 0) / n, 3),
        })
with open(f"{DATA}/part4_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# ---- generic line graph
def plot(fname, title, xlabel, ylabel, xs, series, fmt="{:.2f}",
         default_x=None, default_label=None, ylim=None):
    fig, ax = plt.subplots(figsize=(8.5, 6))
    for sr in series:
        b = sr["bench"]
        dashed = sr.get("dashed", False)
        ax.plot(xs, sr["ys"], linestyle=(0, (4, 2)) if dashed else "-",
                linewidth=2.2, markersize=7, marker=markers[b], color=colors[b],
                markerfacecolor="white" if dashed else colors[b],
                markeredgewidth=1.8, label=sr["label"])
        for x, y in zip(xs, sr["ys"]):
            ax.annotate(fmt.format(y), (x, y), textcoords="offset points",
                        xytext=(0, sr.get("off", 8)), ha="center",
                        fontsize=8, color=colors[b])
    ax.set_xscale("log", base=2)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(x) for x in xs])
    ax.xaxis.set_minor_locator(NullLocator())
    if default_x is not None:
        ax.axvline(default_x, linestyle=":", color="gray", linewidth=1)
        ax.text(default_x * 1.04, 0.98, default_label,
                transform=ax.get_xaxis_transform(), fontsize=8,
                color="gray", va="top")
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, handlelength=4.5, framealpha=0.95)
    plt.tight_layout()
    plt.savefig(f"{DATA}/{fname}", dpi=150)
    plt.close()

def ser(tagf, xs, key, scale=1.0):
    return [{"label": b, "bench": b, "off": 9 if b == "compress95" else -15,
             "ys": [scale * S[(b, tagf(x))][key] for x in xs]} for b in benches]

CAPX = "L1 data-cache capacity (KB) [-cache:dl1 dl1:<sets>:32:4:l], log2 scale"
BLKX = "L1 data-cache block size (bytes) [-cache:dl1 dl1:<sets>:<bsize>:4:l], 16 KB, log2 scale"

# (i) capacity: miss rate and IPC on SEPARATE graphs
plot("part4_g1a_missrate_vs_capacity.png", "Part 4, Graph 1a: dl1 miss rate vs L1 data-cache capacity",
     CAPX, "dl1 miss rate (% of references)", caps,
     ser(cap_tag, caps, "dl1.miss_rate", 100), fmt="{:.2f}%",
     default_x=16, default_label="default config (16 KB)")
plot("part4_g1b_ipc_vs_capacity.png", "Part 4, Graph 1b: IPC vs L1 data-cache capacity",
     CAPX, "IPC (instructions per cycle)", caps,
     ser(cap_tag, caps, "sim_IPC"), default_x=16, default_label="default config (16 KB)")

# (ii) block size
plot("part4_g2a_missrate_vs_block.png", "Part 4, Graph 2a: dl1 miss rate vs L1 data-cache block size",
     BLKX, "dl1 miss rate (% of references)", blks,
     ser(blk_tag, blks, "dl1.miss_rate", 100), fmt="{:.2f}%",
     default_x=32, default_label="default config (32 B)")
plot("part4_g2b_ipc_vs_block.png", "Part 4, Graph 2b: IPC vs L1 data-cache block size",
     BLKX, "IPC (instructions per cycle)", blks,
     ser(blk_tag, blks, "sim_IPC"), default_x=32, default_label="default config (32 B)")

# (iii) CPI vs memory latency, four lines
LATX = "Main-memory first-chunk latency (cycles) [-mem:lat <first> 2], log2 scale"
series = []
for b in benches:
    for l2 in (True, False):
        series.append({"label": f"{b} ({'with L2' if l2 else 'without L2'})", "bench": b,
                       "dashed": not l2, "off": (9 if l2 else -15),
                       "ys": [S[(b, lat_tag(L, l2))]["sim_CPI"] for L in lats]})
plot("part4_g3_cpi_vs_memlat.png", "Part 4, Graph 3: CPI vs main-memory latency, with and without L2",
     LATX, "CPI (cycles per instruction)", lats, series,
     default_x=18, default_label="default (18)")

# extra 4: slowdown from removing the L2
plot("part4_g4_noL2_slowdown.png", "Part 4, Graph 4: slowdown caused by removing the L2",
     LATX, "Slowdown (cycles without L2 / cycles with L2)", lats,
     [{"label": b, "bench": b, "off": 9 if b == "compress95" else -15,
       "ys": [S[(b, lat_tag(L, False))]["sim_cycle"] / S[(b, lat_tag(L, True))]["sim_cycle"]
              for L in lats]} for b in benches],
     default_x=18, default_label="default (18)")

# extra 5: which L1 misses cause the damage (question d)
fig, ax = plt.subplots(figsize=(7, 5))
w = 0.35
for i, (lab, key, col) in enumerate([("il1 (instruction)", "il1_misses_per_1000", "#e8a33d"),
                                      ("dl1 (data)", "dl1_misses_per_1000", "#4a6b7c")]):
    vals = [float(next(r for r in rows if r["benchmark"] == b and r["config"] == lat_tag(100, True))[key])
            for b in benches]
    xs = [j + (i - 0.5) * w for j in range(2)]
    ax.bar(xs, vals, w, label=lab, color=col)
    for x, v in zip(xs, vals):
        ax.text(x, v, f"{v:.1f}", ha="center", va="bottom", fontsize=9)
ax.set_xticks(range(2)); ax.set_xticklabels(benches)
ax.set_xlabel("Benchmark")
ax.set_ylabel("L1 misses per 1000 instructions")
ax.set_title("Part 4, Graph 5: L1 instruction vs data misses (default caches)")
ax.legend()
plt.tight_layout()
plt.savefig(f"{DATA}/part4_g5_il1_vs_dl1_misses.png", dpi=150)
plt.close()

# extra 6: conflict misses (question a)
fig, ax = plt.subplots(figsize=(7, 5))
assoc = [("1-way (direct-mapped)", xtags[0]), ("4-way (default)", cap_tag(16)), ("16-way", xtags[1])]
for i, b in enumerate(benches):
    vals = [100 * S[(b, t)]["dl1.miss_rate"] for _, t in assoc]
    xs = [j + (i - 0.5) * w for j in range(3)]
    ax.bar(xs, vals, w, label=b, color=colors[b])
    for x, v in zip(xs, vals):
        ax.text(x, v, f"{v:.2f}%", ha="center", va="bottom", fontsize=9)
ax.set_xticks(range(3)); ax.set_xticklabels([a for a, _ in assoc])
ax.set_xlabel("L1 data-cache associativity (16 KB, 32 B blocks) [-cache:dl1 dl1:<sets>:32:<assoc>:l]")
ax.set_ylabel("dl1 miss rate (% of references)")
ax.set_title("Part 4, Graph 6: conflict misses (miss rate vs associativity)")
ax.legend()
plt.tight_layout()
plt.savefig(f"{DATA}/part4_g6_associativity.png", dpi=150)
plt.close()

# ---- terminal tables for the write-up
print("\n(a) CAPACITY       KB   dl1miss%   IPC")
for b in benches:
    for K in caps:
        s = S[(b, cap_tag(K))]
        print(f"{b:<11}{K:>8}   {100*s['dl1.miss_rate']:>7.2f}%  {s['sim_IPC']:.3f}")
print("\n(b) BLOCK SIZE      B   dl1miss%   IPC")
for b in benches:
    for B in blks:
        s = S[(b, blk_tag(B))]
        print(f"{b:<11}{B:>8}   {100*s['dl1.miss_rate']:>7.2f}%  {s['sim_IPC']:.3f}")
print("\n(c) MEM LATENCY  lat   CPI(L2)  CPI(noL2)  slowdown")
for b in benches:
    for L in lats:
        a = S[(b, lat_tag(L, True))]; c = S[(b, lat_tag(L, False))]
        print(f"{b:<11}{L:>6}   {a['sim_CPI']:>7.3f}  {c['sim_CPI']:>9.3f}  {c['sim_cycle']/a['sim_cycle']:>7.3f}")
print("\nCPI cost per extra 100 cycles of memory latency (linear fit):")
for b in benches:
    for l2 in (True, False):
        slope = np.polyfit(lats, [S[(b, lat_tag(L, l2))]["sim_CPI"] for L in lats], 1)[0] * 100
        print(f"{b:<11}{'with L2' if l2 else 'no L2':<9} +{slope:.3f} CPI per 100 cycles")
print("\n(d) MISSES PER 1000 INSTR (default caches)  il1    dl1   ul2miss%")
for b in benches:
    s = S[(b, lat_tag(100, True))]; n = s["sim_num_insn"]
    print(f"{b:<11}  il1 {1000*s['il1.misses']/n:>7.2f}   dl1 {1000*s['dl1.misses']/n:>7.2f}   ul2 {100*s['ul2.miss_rate']:.2f}%")
print("\nAssociativity at 16 KB (dl1 miss%):")
for b in benches:
    print(b, [f"{n}: {100*S[(b,t)]['dl1.miss_rate']:.2f}%" for n, t in assoc])
print("\nConsistency: 16 KB / 32 B runs vs Part 3 default (RUU 16) IPC - should match:")
for b in benches:
    p3 = read(f"{RES}/{b}_P3_ruu16.txt")["sim_IPC"]
    print(f"{b:<11} P4a {S[(b, cap_tag(16))]['sim_IPC']:.4f}  P4b {S[(b, blk_tag(32))]['sim_IPC']:.4f}  Part3 {p3:.4f}")
print("\nWrote part4_table.csv and 6 PNG graphs in data/")