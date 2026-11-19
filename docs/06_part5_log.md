# Part 5 log: Branch prediction

## Setup
- Script: scripts/run_P5.sh (12 runs), graphs: scripts/part5_graphs.py
- All runs: default configuration + -max:inst 100000000, only -bpred changes
- Predictors: -bpred perfect | nottaken | bimod -bpred:bimod 512 |
  bimod -bpred:bimod 2048 (default) | 2lev -bpred:2lev 1 1024 8 0 | comb -bpred:comb 1024
- -bpred taken is not used (fetch never redirects on it, so it equals not-taken)
- Raw outputs: results/*_P5_*.txt
- Data: data/part5_table.csv
- Check: the bimod 2048 runs equal the default configuration (compress95 IPC 1.7145
  matches Part 1 and Part 3 RUU 16; cc1 0.8849 matches Part 3 RUU 16).

## Results table

| Benchmark | Predictor | Dir. accuracy | MPKI | IPC | IPC / perfect |
|---|---|---|---|---|---|
| compress95 | Perfect | 100.00% | 0.00 | 2.2347 | 1.000 |
| compress95 | Not-taken | 28.42% | 127.81 | 0.8517 | 0.381 |
| compress95 | Bimodal 512 | 89.91% | 18.01 | 1.7144 | 0.767 |
| compress95 | Bimodal 2048 (default) | 89.92% | 18.00 | 1.7145 | 0.767 |
| compress95 | 2-level GAg | 84.03% | 28.52 | 1.5750 | 0.705 |
| compress95 | Combined | 93.04% | 12.42 | 1.8442 | 0.825 |
| cc1 | Perfect | 100.00% | 0.00 | 1.0055 | 1.000 |
| cc1 | Not-taken | 37.88% | 125.38 | 0.5847 | 0.582 |
| cc1 | Bimodal 512 | 85.97% | 28.33 | 0.8647 | 0.860 |
| cc1 | Bimodal 2048 (default) | 88.51% | 23.19 | 0.8849 | 0.880 |
| cc1 | 2-level GAg | 79.96% | 40.45 | 0.8194 | 0.815 |
| cc1 | Combined | 89.97% | 20.24 | 0.9003 | 0.895 |

MPKI = bpred_<name>.misses / sim_num_insn x 1000. Perfect has no predictor
statistics; its accuracy is 100% and MPKI 0 by definition.

## Graph 1: direction-prediction accuracy (data/part5_g1_dir_rate.png)
[4-6 sentences. Numbers: not-taken is right only 28.4% (compress95) and 37.9% (cc1)
of the time, so most branches are taken (loops). Combined is best on both
(93.0% and 90.0%). 2-level GAg is worse than bimodal on both.]

## Graph 2: IPC normalised to perfect (data/part5_g2_ipc_norm.png)
[4-6 sentences. Numbers: not-taken keeps only 38% (compress95) and 58% (cc1) of
perfect IPC; the best real predictor (combined) keeps 82.5% and 89.5%.]

## Graph 3 (extra): MPKI (data/part5_g3_mpki.png)
[2-3 sentences. MPKI makes predictors comparable across benchmarks.]

## Question (a): how much does static not-taken lose, and why so much on a 4-wide OoO machine?
[Numbers: IPC falls from 2.23 to 0.85 (-62%) on compress95 and from 1.01 to 0.58
(-42%) on cc1. ~126-128 mispredictions per 1000 instructions = one every ~8
instructions. Each one throws away everything fetched after the branch; a
4-wide machine fetches up to 4 per cycle, so it loses up to 4 instructions per
cycle of the penalty, and the window can never fill with useful work.]

## Question (b): bimodal 512 vs 2048, aliasing
[Numbers: compress95 is identical (MPKI 18.01 vs 18.00), so its branches already
fit in 512 counters with no harmful sharing (few, hot branches). cc1 improves
from 28.33 to 23.19 MPKI (accuracy 86.0% -> 88.5%, IPC +2.3%): a compiler has
thousands of static branches, so with 512 counters many unrelated branches
share (alias to) one counter and push it in opposite directions.]

## Question (c): MPKI for every real predictor; which works best and why
[Combined is best for both (12.42 and 20.24 MPKI). GAg with one global
history register is worst of the real dynamic ones (28.52 and 40.45): all
branches share 8 bits of history and the same 1024-entry table, so different
branches that happen to see the same recent history collide, and it needs time
to learn each pattern. Bimodal gives each branch (by address) its own counter.
The combined predictor keeps both and a chooser table (-bpred:comb 1024)
learns, per branch, which one is right more often.]

## Question (d): loss of the best real predictor vs perfect, and why wider/deeper loses more
[Combined loses 17.5% of IPC on compress95 (1.844 vs 2.235) and 10.5% on cc1
(0.900 vs 1.006). compress95 loses more because it has more ILP to lose (Part 2):
a mispredict hurts most when the machine could otherwise have kept 4 units
busy. A wider and deeper machine has more instructions in flight past an
unresolved branch, so each misprediction squashes more work and takes more
cycles to refill.]

## Prediction check (from Part 1)
[Part 1 predicted cc1 would be more branch-sensitive (more branches, higher
MPKI). Result: cc1 does have higher MPKI with every predictor, but compress95
loses MORE IPC (perfect -> default: -23% vs -12%). Say whether the prediction
held and why: cc1 is held back by instruction-cache misses anyway, so fixing
its branches gains less.]

## Observations / problems
- [anything surprising]
