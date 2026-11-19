"""Part 6: candidate table, IPC-vs-cost scatter plot, final vs default.

Performance = geometric mean of IPC over compress95 and cc1.
The final design is FINAL in scripts/p6_designs.py.
"""
import math
import os

import matplotlib.pyplot as plt

from plotlib import BENCHES, COLORS, DATA, RES, load, grouped_bars, write_csv
from p6_designs import DESIGNS, FINAL, BUDGET, cost, describe, options


def done(name):
    return all(os.path.exists(f"{RES}/{b}_P6_{name}.txt") and
               "sim_IPC" in open(f"{RES}/{b}_P6_{name}.txt").read() for b in BENCHES)


rows = []
for name, d in DESIGNS.items():
    total, parts = cost(d)
    if total > BUDGET or not done(name):
        continue
    ipc = {b: load(b, f"P6_{name}")["sim_IPC"] for b in BENCHES}
    rows.append({"design": name, "description": describe(d),
                 "cost": total, **{f"cost_{k}": v for k, v in parts.items()},
                 "IPC_compress95": ipc["compress95"], "IPC_cc1": ipc["cc1"],
                 "geomean_IPC": round(math.sqrt(ipc["compress95"] * ipc["cc1"]), 4),
                 "options": options(d)})
write_csv("part6_candidates.csv", rows)
by = {r["design"]: r for r in rows}
base = by["D00_default"]["geomean_IPC"]

# ---- scatter: geometric-mean IPC vs cost
fig, ax = plt.subplots(figsize=(10, 6.5))
for r in rows:
    special = r["design"] in ("D00_default", FINAL)
    color = "#d64550" if r["design"] == FINAL else "#4a6b7c" if r["design"] == "D00_default" else "#0f8b8d"
    ax.scatter(r["cost"], r["geomean_IPC"], s=110 if special else 55, color=color,
               marker="*" if r["design"] == FINAL else "o", zorder=3,
               edgecolor="black" if special else "none")
# one label per cluster of near-identical points, so names don't overprint
pts = sorted(rows, key=lambda r: (r["cost"], r["geomean_IPC"]))
clusters = []
for r in pts:
    c = clusters[-1] if clusters else None
    if c and c[-1]["cost"] == r["cost"] and r["geomean_IPC"] - c[-1]["geomean_IPC"] < 0.012:
        c.append(r)
    else:
        clusters.append([r])
for c in clusters:
    top = c[-1]
    ax.annotate(", ".join(r["design"].split("_")[0] for r in c),
                (top["cost"], top["geomean_IPC"]), textcoords="offset points",
                xytext=(7, 0), va="center", fontsize=8)
ax.axvline(BUDGET, linestyle="--", color="gray", label=f"Budget ({BUDGET} units)")
ax.scatter([], [], color="#4a6b7c", edgecolor="black", s=110, label="Default configuration (D00)")
ax.scatter([], [], color="#d64550", edgecolor="black", s=110, marker="*", label=f"Final design ({FINAL.split('_')[0]})")
ax.scatter([], [], color="#0f8b8d", s=55, label="Other candidates")
ax.set_title("Part 6: geometric-mean IPC vs cost of every candidate design")
ax.set_xlabel("Cost (units, from the project cost model)")
ax.set_ylabel("Geometric mean of IPC (compress95, cc1)")
ax.grid(alpha=0.3)
ax.legend(fontsize=9, loc="lower right")
plt.tight_layout()
plt.savefig(f"{DATA}/part6_g1_ipc_vs_cost.png", dpi=150)
plt.close()

# ---- final vs default, per benchmark
f, dflt = by[FINAL], by["D00_default"]
grouped_bars("part6_g2_final_vs_default.png",
             f"Part 6: final design ({FINAL.split('_')[0]}, cost {f['cost']:g}) vs default (cost {dflt['cost']:g})",
             "Configuration", "IPC (instructions per cycle)",
             ["Default", "Final design"],
             {"compress95": [dflt["IPC_compress95"], f["IPC_compress95"]],
              "cc1": [dflt["IPC_cc1"], f["IPC_cc1"]]}, fmt="{:.3f}")

print(f"\n{'design':<26} {'cost':>6}  {'compress95':>10} {'cc1':>7} {'geomean':>8}  vs default")
for r in sorted(rows, key=lambda r: r["geomean_IPC"]):
    print(f"{r['design']:<26} {r['cost']:>6.2f}  {r['IPC_compress95']:>10.4f} {r['IPC_cc1']:>7.4f} "
          f"{r['geomean_IPC']:>8.4f}  {100*(r['geomean_IPC']/base-1):+.1f}%")
print(f"\nFinal design {FINAL}: {describe(DESIGNS[FINAL])}")
total, parts = cost(DESIGNS[FINAL])
for k, v in parts.items():
    print(f"  {k:<6} {v:g}")
print(f"  total  {total:g} / {BUDGET}")
print("\nWrote part6_candidates.csv and 2 graphs in data/")
