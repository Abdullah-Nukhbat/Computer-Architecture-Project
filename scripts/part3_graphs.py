import re, csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

RES = "/mnt/d/CA_Project/results"
DATA = "/mnt/d/CA_Project/data"
benches = ["compress95", "cc1"]
sizes = [4, 8, 16, 32, 64, 128]
colors = {"compress95": "#0f8b8d", "cc1": "#d64550"}
markers = {"compress95": "o", "cc1": "s"}

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
    for k in ("sim_IPC", "sim_cycle", "ruu_occupancy", "ruu_full"):
        if k not in s:
            raise SystemExit(f"{k} not found in {path}")
    return s

D = {}
rows = []
for b in benches:
    for R in sizes:
        s = load(f"{RES}/{b}_P3_ruu{R}.txt")
        D[(b, R)] = s
        rows.append({
            "benchmark": b, "ruu_size": R, "lsq_size": R // 2,
            "sim_num_insn": int(s["sim_num_insn"]),
            "sim_cycle": int(s["sim_cycle"]),
            "sim_IPC": s["sim_IPC"], "sim_CPI": s["sim_CPI"],
            "ruu_occupancy": s["ruu_occupancy"],
            "occupancy_pct_of_ruu": round(100 * s["ruu_occupancy"] / R, 1),
            "ruu_full": s["ruu_full"],
            "bpred_dir_rate": s.get("bpred_bimod.bpred_dir_rate", ""),
        })
with open(f"{DATA}/part3_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# extra runs for question (c)
C = {}
for b in benches:
    C[b] = load(f"{RES}/{b}_P3c_W8_ruu16.txt")
with open(f"{DATA}/part3c_table.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["benchmark", "design", "sim_IPC", "sim_cycle"])
    for b in benches:
        w.writerow([b, "W=8, RUU 16", C[b]["sim_IPC"], int(C[b]["sim_cycle"])])
        w.writerow([b, "W=4, RUU 64", D[(b, 64)]["sim_IPC"], int(D[(b, 64)]["sim_cycle"])])

XLABEL = "RUU size (entries) [-ruu:size], log2 scale; LSQ = RUU/2 [-lsq:size]"

def line_graph(fname, title, ylabel, getter, xvals=None, fmt="{:.2f}",
               ylog2=False, ref=None, ref_label=None, ylim=None, xlabel=XLABEL):
    xv = xvals or sizes
    fig, ax = plt.subplots(figsize=(8.5, 6))
    for b in benches:
        ys = [getter(b, R) for R in xv]
        ax.plot(xv, ys, linestyle="-", linewidth=2.2, markersize=7,
                marker=markers[b], color=colors[b], label=b)
        off = 8 if b == "compress95" else -14
        for x, y in zip(xv, ys):
            ax.annotate(fmt.format(y), (x, y), textcoords="offset points",
                        xytext=(0, off), ha="center", fontsize=8, color=colors[b])
    if ref:
        ax.plot(sizes, [ref(R) for R in sizes], ":", color="gray", label=ref_label)
    ax.set_xscale("log", base=2)
    ax.set_xticks(xv)
    ax.set_xticklabels([str(R) for R in xv])
    ax.xaxis.set_minor_locator(NullLocator())
    if ylog2:
        ax.set_yscale("log", base=2)
    if ylim:
        ax.set_ylim(*ylim)
    if 16 in xv:
        ax.axvline(16, linestyle=":", color="gray", linewidth=1)
        ax.text(16.3, 0.98, "default config (RUU 16)", transform=ax.get_xaxis_transform(),
                fontsize=8, color="gray", va="top")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, handlelength=4.5, framealpha=0.95)
    plt.tight_layout()
    plt.savefig(f"{DATA}/{fname}", dpi=150)
    plt.close()

# Graph 1 (required): IPC vs RUU size
line_graph("part3_g1_ipc_vs_ruu.png", "Part 3, Graph 1: IPC vs RUU size (width 4)",
           "IPC (instructions per cycle)", lambda b, R: D[(b, R)]["sim_IPC"])

# Graph 2 (required): average RUU occupancy
line_graph("part3_g2_ruu_occupancy.png",
           "Part 3, Graph 2: average RUU occupancy vs RUU size",
           "Average RUU occupancy (entries, log2 scale)",
           lambda b, R: D[(b, R)]["ruu_occupancy"], fmt="{:.1f}", ylog2=True,
           ref=lambda R: R, ref_label="RUU size (window completely full)")

# Graph 3 (required): fraction of cycles the RUU was full
line_graph("part3_g3_ruu_full.png",
           "Part 3, Graph 3: fraction of cycles the RUU was full",
           "Cycles with RUU full (% of all cycles)",
           lambda b, R: 100 * D[(b, R)]["ruu_full"], fmt="{:.1f}%", ylim=(-5, 105))

# Graph 4 (extra): gain from each doubling
def gain(b, R):
    prev = R // 2
    return 100 * (D[(b, R)]["sim_IPC"] / D[(b, prev)]["sim_IPC"] - 1)
line_graph("part3_g4_gain_per_doubling.png",
           "Part 3, Graph 4: IPC gain from each doubling of the RUU",
           "IPC gain over the next-smaller RUU (%)", gain, xvals=sizes[1:], fmt="{:.1f}%",
           xlabel="RUU size reached by the doubling (entries) [-ruu:size], log2 scale")

# Graph 5 (extra, question c): W=8/RUU16 vs W=4/RUU64
fig, ax = plt.subplots(figsize=(7, 5))
width = 0.35
designs = [("W=8, RUU 16", lambda b: C[b]["sim_IPC"], "#e8a33d"),
           ("W=4, RUU 64", lambda b: D[(b, 64)]["sim_IPC"], "#4a6b7c")]
for i, (name, g, col) in enumerate(designs):
    vals = [g(b) for b in benches]
    xs = [j + (i - 0.5) * width for j in range(len(benches))]
    ax.bar(xs, vals, width, label=name, color=col)
    for x, v in zip(xs, vals):
        ax.text(x, v, f"{v:.2f}", ha="center", va="bottom", fontsize=9)
ax.set_xticks(range(len(benches)))
ax.set_xticklabels(benches)
ax.set_xlabel("Benchmark")
ax.set_ylabel("IPC (instructions per cycle)")
ax.set_title("Part 3, Graph 5: W=8 with RUU 16 vs W=4 with RUU 64")
ax.legend()
plt.tight_layout()
plt.savefig(f"{DATA}/part3_g5_design_choice.png", dpi=150)
plt.close()

# Terminal table for your write-up
print("\nbenchmark   RUU  LSQ   IPC     occupancy  occ%RUU  full%")
for b in benches:
    for R in sizes:
        s = D[(b, R)]
        print(f"{b:<11}{R:>4}{R//2:>5}  {s['sim_IPC']:>6.3f}  {s['ruu_occupancy']:>9.2f}  "
              f"{100*s['ruu_occupancy']/R:>6.1f}%  {100*s['ruu_full']:>5.1f}%")
print("\nQuestion (c):")
for b in benches:
    print(f"{b:<11} W=8/RUU16 IPC {C[b]['sim_IPC']:.3f}   W=4/RUU64 IPC {D[(b,64)]['sim_IPC']:.3f}")
print("\nConsistency check against Part 2 (W=4 out-of-order, RUU 64) - should match:")
for b in benches:
    p2 = read(f"{RES}/{b}_P2_W4_ooo.txt")["sim_IPC"]
    print(f"{b:<11} Part 3 {D[(b,64)]['sim_IPC']:.4f}   Part 2 {p2:.4f}")
print("\nWrote part3_table.csv, part3c_table.csv and 5 PNG graphs in data/")