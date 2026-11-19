"""Part 5: branch prediction graphs and MPKI table.

Required graphs: (i) direction-prediction accuracy per predictor,
(ii) IPC per predictor normalised to the perfect predictor.
Extra: MPKI per real predictor (question c).
"""
from plotlib import BENCHES, load, grouped_bars, write_csv

# (tag, label, statistics prefix in the output file)
PREDS = [("P5_perfect", "Perfect", None),
         ("P5_nottaken", "Not-taken", "bpred_nottaken"),
         ("P5_bimod512", "Bimodal 512", "bpred_bimod"),
         ("P5_bimod2048", "Bimodal 2048\n(default)", "bpred_bimod"),
         ("P5_2lev", "2-level GAg\n(1, 1024, 8)", "bpred_2lev"),
         ("P5_comb", "Combined\n(1024)", "bpred_comb")]

D = {(b, t): load(b, t) for b in BENCHES for t, _, _ in PREDS}


def dir_rate(b, tag, pre):
    return 1.0 if pre is None else D[(b, tag)][f"{pre}.bpred_dir_rate"]


def mpki(b, tag, pre):
    s = D[(b, tag)]
    return 0.0 if pre is None else 1000 * s[f"{pre}.misses"] / s["sim_num_insn"]


rows = []
for b in BENCHES:
    perfect = D[(b, "P5_perfect")]["sim_IPC"]
    for tag, label, pre in PREDS:
        s = D[(b, tag)]
        rows.append({"benchmark": b, "predictor": label.replace("\n", " "),
                     "sim_num_insn": int(s["sim_num_insn"]),
                     "sim_cycle": int(s["sim_cycle"]),
                     "sim_IPC": s["sim_IPC"], "sim_CPI": s["sim_CPI"],
                     "bpred_dir_rate": round(dir_rate(b, tag, pre), 4),
                     "misses": 0 if pre is None else int(s[f"{pre}.misses"]),
                     "MPKI": round(mpki(b, tag, pre), 2),
                     "IPC_vs_perfect": round(s["sim_IPC"] / perfect, 4)})
write_csv("part5_table.csv", rows)

labels = [label for _, label, _ in PREDS]
grouped_bars("part5_g1_dir_rate.png",
             "Part 5, Graph 1: branch direction-prediction accuracy",
             "Branch predictor [-bpred]", "Direction-prediction accuracy (%)",
             labels, {b: [100 * dir_rate(b, t, p) for t, _, p in PREDS] for b in BENCHES},
             fmt="{:.1f}%", ylim=(50, 105), highlight=3)
grouped_bars("part5_g2_ipc_norm.png",
             "Part 5, Graph 2: IPC normalised to the perfect predictor",
             "Branch predictor [-bpred]", "IPC / IPC with perfect prediction",
             labels, {b: [r["IPC_vs_perfect"] for r in rows if r["benchmark"] == b]
                      for b in BENCHES},
             fmt="{:.3f}", ylim=(0, 1.1), hline=1.0, hline_label="Perfect prediction",
             highlight=3)
real = PREDS[1:]
grouped_bars("part5_g3_mpki.png",
             "Part 5, Graph 3: mispredictions per 1000 instructions (MPKI)",
             "Branch predictor [-bpred]", "MPKI (misses / instructions x 1000)",
             [l for _, l, _ in real], {b: [mpki(b, t, p) for t, _, p in real] for b in BENCHES},
             fmt="{:.1f}", highlight=2)

print("\nbenchmark   predictor                 dir rate   MPKI    IPC     IPC/perfect")
for r in rows:
    print(f"{r['benchmark']:<11} {r['predictor']:<25} {100*r['bpred_dir_rate']:>6.2f}%  "
          f"{r['MPKI']:>6.2f}  {r['sim_IPC']:.4f}  {r['IPC_vs_perfect']:.3f}")
print("\nWrote part5_table.csv and 3 graphs in data/")
