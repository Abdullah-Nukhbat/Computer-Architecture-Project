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
Static not-taken prediction is right only 28.4% of the time for compress95 and
37.9% for cc1, so 72% and 62% of the branches in these programs are taken, mostly
loop branches jumping back. All the dynamic predictors are far better: bimodal
reaches 89.9% (compress95) and 86.0 to 88.5% (cc1), and the combined predictor
is the best on both at 93.0% and 90.0%. The two-level GAg predictor is the worst
dynamic predictor on both (84.0% and 80.0%), worse even than a 512-entry bimodal
table. compress95 is more predictable than cc1 with every dynamic predictor,
because its branches belong to one compression loop that repeats the same
decisions, while a compiler's branches depend on the program it is compiling.
Accuracy only counts branches, however; Graph 3 converts it into mispredictions
per instruction, which is what determines lost cycles.

## Graph 2: IPC normalised to perfect (data/part5_g2_ipc_norm.png)
With perfect prediction compress95 reaches IPC 2.235 and cc1 1.006. Not-taken
keeps only 38.1% and 58.2% of that, bimodal 2048 (the default) 76.7% and 88.0%,
and the combined predictor 82.5% and 89.5%. Every real predictor costs
compress95 a bigger fraction of its performance than cc1, even though cc1
mispredicts more often. compress95 has much more ILP (Part 2), so each
misprediction interrupts a machine that would otherwise run 2+ instructions per
cycle; cc1 is also held back by instruction-cache misses, so removing its
mispredictions gains less. The best real predictor still leaves 17.5% of
compress95's performance and 10.5% of cc1's on the table.

## Graph 3 (extra): MPKI (data/part5_g3_mpki.png)
MPKI combines accuracy with how often branches occur, so it compares
predictors and benchmarks fairly. Not-taken mispredicts about 126 to 128 times
per 1000 instructions on both programs, 7.1 and 5.4 times more than the default
bimodal.
Among the real dynamic predictors the order is the same for both programs:
combined (12.4, 20.2) is best, then bimodal 2048 (18.0, 23.2), then bimodal 512
(18.0, 28.3), and two-level GAg is worst (28.5, 40.5).

## Question (a): how much does static not-taken lose, and why so much on a 4-wide OoO machine?
Not-taken prediction lowers IPC from 2.235 to 0.852 (-62%) on compress95 and from
1.006 to 0.585 (-42%) on cc1 compared with perfect prediction. It mispredicts
127.8 and 125.4 times per 1000 instructions, which is once every 8 instructions.
Each misprediction costs the time to resolve the branch plus a 3-cycle refetch
penalty (-fetch:mplat 3), and every instruction fetched after the branch is
squashed. A 4-wide machine fetches 4 instructions per cycle, so it reaches the
next mispredicted branch after about 2 fetch cycles: the window never fills with
useful work, and the out-of-order core, whose whole advantage is looking far
ahead, cannot look past the next taken branch. The wider the machine, the more
instructions each wasted cycle costs, so a free predictor is a very expensive
choice for a 4-wide out-of-order core.

## Question (b): bimodal 512 vs 2048, aliasing
For compress95, the two sizes give the same result (18.01 against 18.00 MPKI,
IPC 1.7144 against 1.7145). Its few hot branches already have their own counters
in a 512-entry table, so a bigger table changes nothing. For cc1, 2048 entries
lower MPKI from 28.33 to 23.19 (accuracy 86.0% to 88.5%) and raise IPC by 2.3%. A
compiler has thousands of static branches, and the bimodal table is indexed by
the low bits of the branch address, so with only 512 counters many unrelated
branches share (alias to) the same counter. When one is mostly taken and the
other mostly not taken, they keep pushing the shared counter in opposite
directions and both are mispredicted. Four times as many counters means far
fewer branches share one, which removes most of this aliasing.

## Question (c): MPKI for every real predictor; which works best and why
| Predictor | compress95 MPKI | cc1 MPKI |
|---|---|---|
| Not-taken | 127.81 | 125.38 |
| Bimodal 512 | 18.01 | 28.33 |
| Bimodal 2048 | 18.00 | 23.19 |
| 2-level GAg (1, 1024, 8) | 28.52 | 40.45 |
| Combined (1024) | 12.42 | 20.24 |

The combined predictor works best for both benchmarks. The two-level GAg
predictor uses one global history register of 8 bits for all branches, and those
8 bits alone choose the counter. Unrelated branches that happen to see the same
recent outcomes therefore share a counter, which is aliasing between branches,
and a branch that is simply biased (almost always taken) has its outcome spread
over many history patterns that each have to be learned separately. Bimodal,
indexed by branch address, gives each biased branch its own counter, which is why
it beats GAg on both programs (18.0 against 28.5 and 23.2 against 40.5 MPKI). The
combined predictor runs both a bimodal and a two-level predictor and keeps a
1024-entry table of 2-bit choosers, indexed by branch address, that learns for
each branch which predictor has been right more often. Biased branches use the
bimodal side, while branches correlated with earlier branches use the history
side, so it beats both (12.4 and 20.2 MPKI).

## Question (d): loss of the best real predictor vs perfect, and why wider/deeper loses more
The best real predictor (combined) loses 17.5% of IPC on compress95 (1.844
against 2.235) and 10.5% on cc1 (0.900 against 1.006). A wider, deeper
out-of-order machine has more instructions in flight between fetching a branch
and resolving it: more fetched per cycle, and more cycles from fetch to
execution. Every one of them is squashed on a misprediction, and a deeper
pipeline also takes more cycles to refill. A wider machine also wastes more
issue slots per lost cycle. So the same 12 to 20 MPKI cost more performance the
more aggressive the core is; in Part 6, the design that adds width and RUU also
needs the best predictor.

## Prediction check (from Part 1)
Our Part 1 prediction was only half right. cc1 does mispredict more with every
real predictor (for example 23.2 against 18.0 MPKI with the default bimodal), but
compress95 loses more performance to mispredictions: the default predictor costs
it 23% of perfect-prediction IPC against 12% for cc1. We expected the program with
more and harder branches to be more sensitive, but sensitivity also depends on
what else limits the program. compress95 has a lot of ILP that mispredictions
waste, while cc1 is limited by instruction-cache misses, so better branch
prediction helps it less.

## Observations / problems
- bimod 2048 is the default predictor, so those runs match the default
  configuration exactly (compress95 1.7145, cc1 0.8849).
- The perfect predictor prints no bpred_* statistics; its accuracy is 100% and
  its MPKI 0 by definition.
