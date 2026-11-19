"""Collect every raw output file in results/ into data/all_runs.csv,
one row per run, as the submission requires.
"""
import csv
import glob
import os
import re

from paths import RES, DATA


def parse(path):
    stats, cmd = {}, ""
    for line in open(path):
        if line.startswith("sim: command line:"):
            cmd = line.split(":", 2)[2].strip()
        m = re.match(r"^(\S+)\s+([-0-9.eE+]+)\s", line)
        if m:
            stats[m.group(1)] = float(m.group(2))
    return stats, cmd


def options_only(cmd):
    """The options from the command line, without paths."""
    cmd = re.sub(r"^\S*sim-outorder\s*", "", cmd)
    cmd = re.sub(r"-redir:sim\s+\S+\s*", "", cmd)
    return re.sub(r"\.\./Programs/\S+.*$", "", cmd).strip() or "(default)"


rows = []
for path in sorted(glob.glob(f"{RES}/*.txt")):
    name = os.path.basename(path)[:-4]
    m = re.match(r"^(compress95|cc1)_(P\d)([a-z]?)_?(.*)$", name)
    if not m:
        continue                      # e.g. P1_diff.txt
    s, cmd = parse(path)
    if "sim_IPC" not in s:
        continue
    bench, part, sub, tag = m.groups()
    n = s["sim_num_insn"]
    pred = next((k[: -len(".bpred_dir_rate")] for k in s if k.endswith(".bpred_dir_rate")), None)
    rows.append({
        "file": os.path.basename(path), "benchmark": bench,
        "part": part[1:] + sub, "config": tag or "default",
        "options": options_only(cmd),
        "sim_num_insn": int(n), "sim_cycle": int(s["sim_cycle"]),
        "sim_IPC": s["sim_IPC"], "sim_CPI": s["sim_CPI"],
        "loads_pct": round(100 * s["sim_num_loads"] / n, 2),
        "stores_pct": round(100 * s["sim_num_stores"] / n, 2),
        "branches_pct": round(100 * s["sim_num_branches"] / n, 2),
        "il1_miss_rate": s.get("il1.miss_rate", ""),
        "dl1_miss_rate": s.get("dl1.miss_rate", ""),
        "ul2_miss_rate": s.get("ul2.miss_rate", ""),
        "predictor": pred.replace("bpred_", "") if pred else "perfect",
        "bpred_dir_rate": s.get(f"{pred}.bpred_dir_rate", "") if pred else 1.0,
        "bpred_misses": int(s[f"{pred}.misses"]) if pred else 0,
        "MPKI": round(1000 * s[f"{pred}.misses"] / n, 2) if pred else 0.0,
        "ruu_occupancy": s.get("ruu_occupancy", ""),
        "ruu_full": s.get("ruu_full", ""),
        "lsq_occupancy": s.get("lsq_occupancy", ""),
    })

order = {"compress95": 0, "cc1": 1}
rows.sort(key=lambda r: (r["part"], order[r["benchmark"]], r["file"]))
with open(f"{DATA}/all_runs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print(f"Wrote data/all_runs.csv with {len(rows)} runs")
