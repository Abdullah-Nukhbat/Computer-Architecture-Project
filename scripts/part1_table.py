import re, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paths import RES, DATA  # reads .env (defaults: repo results/ and data/)
benches = ["compress95", "cc1"]

def read(path):
    d = {}
    for line in open(path):
        m = re.match(r"^(\S+)\s+([-0-9.eE+]+)\s", line)
        if m:
            d[m.group(1)] = float(m.group(2))
    return d

rows = []
for b in benches:
    s = read(f"{RES}/{b}_P1.txt")
    n = s["sim_num_insn"]
    acc = s["bpred_bimod.bpred_dir_rate"]
    rows.append({
        "benchmark": b,
        "sim_num_insn": int(n),
        "sim_cycle": int(s["sim_cycle"]),
        "sim_IPC": s["sim_IPC"],
        "sim_CPI": s["sim_CPI"],
        "loads_pct": round(100 * s["sim_num_loads"] / n, 2),
        "stores_pct": round(100 * s["sim_num_stores"] / n, 2),
        "branches_pct": round(100 * s["sim_num_branches"] / n, 2),
        "il1_miss_rate": s["il1.miss_rate"],
        "dl1_miss_rate": s["dl1.miss_rate"],
        "ul2_miss_rate": s["ul2.miss_rate"],
        "bpred_dir_rate": acc,
        "MPKI": round((1 - acc) * s["sim_num_branches"] / n * 1000, 2),
    })
for r in rows:
    r["other_pct"] = round(100 - r["loads_pct"] - r["stores_pct"] - r["branches_pct"], 2)

with open(f"{DATA}/part1_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# stacked bar chart of the instruction mix
cats = [("loads_pct", "Loads"), ("stores_pct", "Stores"),
        ("branches_pct", "Branches"), ("other_pct", "Other")]
fig, ax = plt.subplots(figsize=(6, 5))
bottom = [0, 0]
for key, label in cats:
    vals = [r[key] for r in rows]
    ax.bar(benches, vals, bottom=bottom, label=label)
    for i, v in enumerate(vals):
        ax.text(i, bottom[i] + v / 2, f"{v:.1f}%", ha="center", va="center")
    bottom = [bottom[i] + vals[i] for i in range(2)]
ax.set_title("Part 1: Instruction mix")
ax.set_ylabel("Share of committed instructions (%)")
ax.set_xlabel("Benchmark")
ax.legend()
plt.tight_layout()
plt.savefig(f"{DATA}/part1_instruction_mix.png", dpi=150)
print("Wrote part1_table.csv and part1_instruction_mix.png")
for r in rows:
    print(r)