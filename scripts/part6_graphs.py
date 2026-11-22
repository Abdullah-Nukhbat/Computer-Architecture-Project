import os, re, csv, math, stat
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from part6_designs import *

DATA = ROOT + "/data"
CFG = ROOT + "/configs"
os.makedirs(DATA, exist_ok=True); os.makedirs(CFG, exist_ok=True)

def read(path):
    d = {}
    for line in open(path):
        m = re.match(r"^(\S+)\s+([-0-9.eE+]+)\s", line)
        if m:
            d[m.group(1)] = float(m.group(2))
    return d

rows = []
for dz in DESIGNS:
    if problems(dz):
        continue
    ipc = {}
    for b in BENCHES:
        p = "%s/%s_P6_%s.txt" % (RES, b, dz["name"])
        if not os.path.exists(p) or "sim_IPC" not in read(p):
            print("missing results for", dz["name"], b); break
        ipc[b] = read(p)["sim_IPC"]
    else:
        gm = math.prod(ipc.values()) ** (1 / len(ipc))
        rows.append(dict(dz=dz, name=dz["name"], cost=cost(dz), ipc=ipc, gm=gm))
if not rows:
    raise SystemExit("no finished designs")
default = rows[0]
assert default["name"] == DESIGNS[0]["name"]
for r in rows:
    r["gain"] = 100 * (r["gm"] / default["gm"] - 1)
by_name = {r["name"]: r for r in rows}
if FINAL_NAME:
    if FINAL_NAME not in by_name:
        raise SystemExit("FINAL_NAME not found among finished designs")
    final = by_name[FINAL_NAME]
else:
    final = max(rows, key=lambda r: r["gm"])

# ---- CSV
with open(DATA + "/part6_table.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["design", "W", "ruu", "il1", "dl1", "l2", "bpred", "cost",
                "ipc_compress95", "ipc_cc1", "geomean_ipc", "gain_vs_default_pct", "note"])
    for r in sorted(rows, key=lambda r: r["cost"]):
        z = r["dz"]
        w.writerow([r["name"], z["W"], z["ruu"], z["il1"], z["dl1"], z["l2"], z["bp"],
                    round(r["cost"], 2), r["ipc"]["compress95"], r["ipc"]["cc1"],
                    round(r["gm"], 4), round(r["gain"], 2), z["note"]])

# ---- Graph 1: scatter IPC vs cost
fig, ax = plt.subplots(figsize=(10, 6.5))
for r in rows:
    if r is default: col, mk, sz, lab = "#888888", "D", 90, "default (cost 86)"
    elif r is final: col, mk, sz, lab = "#e8a33d", "*", 260, "final design"
    else: col, mk, sz, lab = "#0f8b8d", "o", 60, "candidate"
    ax.scatter(r["cost"], r["gm"], c=col, marker=mk, s=sz, zorder=3, label=lab)
    ax.annotate(r["name"][:3], (r["cost"], r["gm"]), textcoords="offset points",
                xytext=(6, 6), fontsize=9)
pts = sorted(rows, key=lambda r: r["cost"]); best = 0; fx, fy = [], []
for r in pts:
    if r["gm"] > best:
        best = r["gm"]; fx.append(r["cost"]); fy.append(best)
ax.step(fx, fy, where="post", linestyle="--", color="gray", label="best IPC so far (frontier)")
ax.axvline(BUDGET, color="#d64550", linestyle=":", label="budget (100 units)")
h, l = ax.get_legend_handles_labels()
seen = {}
for hh, ll in zip(h, l): seen.setdefault(ll, hh)
ax.legend(seen.values(), seen.keys(), fontsize=9)
ax.set_xlabel("Hardware cost (units, statement cost model)")
ax.set_ylabel("Geometric-mean IPC (compress95, cc1)")
ax.set_title("Part 6, Graph 1: performance vs cost of every candidate design")
ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(DATA + "/part6_g1_scatter.png", dpi=150); plt.close()

# ---- Graph 2: bars per design
order = sorted(rows, key=lambda r: r["cost"])
fig, ax = plt.subplots(figsize=(12, 6.5)); w = 0.27
series = [("compress95", lambda r: r["ipc"]["compress95"], "#0f8b8d"),
          ("cc1", lambda r: r["ipc"]["cc1"], "#d64550"),
          ("geometric mean", lambda r: r["gm"], "#888888")]
for i, (lab, g, col) in enumerate(series):
    xs = [j + (i - 1) * w for j in range(len(order))]
    vals = [g(r) for r in order]
    ax.bar(xs, vals, w, label=lab, color=col)
    for x, v in zip(xs, vals):
        ax.text(x, v, "%.2f" % v, ha="center", va="bottom", fontsize=7)
ax.set_xticks(range(len(order)))
ax.set_xticklabels(["%s\ncost %.1f" % (r["name"][:3], r["cost"]) for r in order], fontsize=8)
ax.set_xlabel("Design (sorted by cost)")
ax.set_ylabel("IPC (instructions per cycle)")
ax.set_title("Part 6, Graph 2: IPC of every candidate design")
ax.legend(); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(DATA + "/part6_g2_bars.png", dpi=150); plt.close()

# ---- Graph 3: default vs final
fig, ax = plt.subplots(figsize=(8, 5.5)); w = 0.35
groups = BENCHES + ["geometric mean"]
for i, (r, col) in enumerate([(default, "#888888"), (final, "#e8a33d")]):
    vals = [r["ipc"][b] for b in BENCHES] + [r["gm"]]
    xs = [j + (i - 0.5) * w for j in range(3)]
    ax.bar(xs, vals, w, color=col, label="%s (cost %.1f)" % (r["name"], r["cost"]))
    for x, v in zip(xs, vals):
        ax.text(x, v, "%.3f" % v, ha="center", va="bottom", fontsize=9)
ax.set_xticks(range(3)); ax.set_xticklabels(groups)
ax.set_xlabel("Benchmark"); ax.set_ylabel("IPC (instructions per cycle)")
ax.set_title("Part 6, Graph 3: final design vs default configuration")
ax.legend(); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig(DATA + "/part6_g3_final_vs_default.png", dpi=150); plt.close()

# ---- Graph 4: cost breakdown
fig, ax = plt.subplots(figsize=(7.5, 5.5))
labels = ["Width", "RUU", "L1 I-cache", "L1 D-cache", "L2", "Branch predictor"]
cols = ["#4a6b7c", "#0f8b8d", "#e8a33d", "#d64550", "#8e6bbf", "#888888"]
for i, r in enumerate([default, final]):
    bottom = 0
    for (lab, c), col, nm in zip(cost_lines(r["dz"]), cols, labels):
        ax.bar(i, c, 0.5, bottom=bottom, color=col, label=nm if i == 0 else None)
        if c > 2: ax.text(i, bottom + c / 2, "%.1f" % c, ha="center", va="center", fontsize=8, color="white")
        bottom += c
    ax.text(i, bottom + 1, "%.1f" % bottom, ha="center", fontsize=10)
ax.axhline(BUDGET, color="#d64550", linestyle=":", label="budget (100)")
ax.set_xticks([0, 1]); ax.set_xticklabels(["default", final["name"]])
ax.set_xlabel("Design"); ax.set_ylabel("Cost (units)")
ax.set_title("Part 6, Graph 4: where the budget is spent")
ax.legend(fontsize=8, ncol=2); ax.set_ylim(0, 115)
plt.tight_layout(); plt.savefig(DATA + "/part6_g4_cost_breakdown.png", dpi=150); plt.close()

# ---- final cost file (line by line)
fz = final["dz"]
with open(DATA + "/part6_final_cost.md", "w") as f:
    f.write("# Final design %s\n\n| Component | Cost |\n|---|---|\n" % final["name"])
    for lab, c in cost_lines(fz):
        f.write("| %s | %.2f |\n" % (lab, c))
    f.write("| **Total** | **%.2f** (budget 100) |\n\n" % final["cost"])
    f.write("| | default | final |\n|---|---|---|\n")
    for b in BENCHES:
        f.write("| IPC %s | %.4f | %.4f |\n" % (b, default["ipc"][b], final["ipc"][b]))
    f.write("| Geometric-mean IPC | %.4f | %.4f |\n" % (default["gm"], final["gm"]))

# ---- config file and verification script
toks = options(fz); cfg = ["# Part 6 final design: %s (cost %.2f)" % (final["name"], final["cost"])]
for t in toks:
    if t.startswith("-"): cfg.append(t)
    else: cfg[-1] += " " + t
open(CFG + "/final_design.cfg", "w").write("\n".join(cfg) + "\n")
sh = ["#!/bin/bash", "# re-runs the final design through -config (what the TA will do)",
      "cd %s || exit 1" % INPUT,
      "env -i %s -config %s/configs/final_design.cfg -redir:sim %s/compress95_P6v_final_cfg.txt ../Programs/compress95.ss < compress95.in > /dev/null" % (SIM, ROOT, RES),
      "env -i %s -config %s/configs/final_design.cfg -redir:sim %s/cc1_P6v_final_cfg.txt ../Programs/cc1.ss -O 1stmt.i > /dev/null" % (SIM, ROOT, RES),
      'grep "^sim_IPC" %s/compress95_P6v_final_cfg.txt %s/cc1_P6v_final_cfg.txt' % (RES, RES),
      'grep "^sim_IPC" %s/compress95_P6_%s.txt %s/cc1_P6_%s.txt' % (RES, final["name"], RES, final["name"])]
open(ROOT + "/scripts/run_final_cfg.sh", "w").write("\n".join(sh) + "\n")
os.chmod(ROOT + "/scripts/run_final_cfg.sh", 0o755)

# ---- terminal output
print("\n%-24s %6s %9s %7s %8s %8s" % ("design", "cost", "compress95", "cc1", "geomean", "vs def"))
for r in sorted(rows, key=lambda r: r["cost"]):
    tag = "  <- FINAL" if r is final else ""
    print("%-24s %6.2f %9.4f %9.4f %8.4f %+7.1f%%%s" % (
        r["name"], r["cost"], r["ipc"]["compress95"], r["ipc"]["cc1"], r["gm"], r["gain"], tag))
print("\nRanked by geometric-mean IPC:")
for r in sorted(rows, key=lambda r: -r["gm"])[:5]:
    print("  %-24s %.4f (cost %.2f)  %s" % (r["name"], r["gm"], r["cost"], r["dz"]["note"]))
print("\nFinal design cost, line by line:")
for lab, c in cost_lines(fz):
    print("  %-46s %6.2f" % (lab, c))
print("  %-46s %6.2f" % ("TOTAL", final["cost"]))
print("\nWrote data/part6_table.csv, part6_final_cost.md, 4 PNG graphs,"
      " configs/final_design.cfg, scripts/run_final_cfg.sh")