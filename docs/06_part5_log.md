# Part 5 log: Branch prediction

## Setup
- Scripts: scripts/run_P5.sh (12 required runs + 8 extra), scripts/part5_graphs.py
- Fixed: -max:inst 100000000, default width 4, RUU 16, LSQ 8
- Predictors: perfect, nottaken, bimod 512, bimod 2048 (default),
  2lev GAg (-bpred:2lev 1 1024 8 0), comb (-bpred:comb 1024)
- -bpred taken NOT used (statement: same result as not-taken in sim-outorder)
- Perfect prints no predictor statistics: accuracy = 100%, misses = 0 by definition
- MPKI = <predictor>.misses / sim_num_insn x 1000
- Extra (question d): perfect predictor at W = 1, 2, 4, 8 (RUU 64, LSQ 32),
  compared with the Part 2 out-of-order runs (bimodal 2048)
- Raw outputs: results/*_P5_*.txt and results/*_P5x_*.txt
- Data: data/part5_table.csv, data/part5x_table.csv
- Check: bimod 2048 matches the Part 3 RUU 16 run

## Results tables
[paste the tables printed by part5_graphs.py]

## Graph 1: direction-prediction accuracy
[4-6 sentences. Numbers first: the accuracy of each predictor for each
benchmark. Then why. Compare the benchmarks. End with a design conclusion.]

## Graph 2: IPC normalized to perfect
[4-6 sentences. Numbers first (best and worst predictor), then why.]

## Graph 3: MPKI
[3-5 sentences. State the MPKI of each real predictor and which is best.]

## Graph 5: CPI vs MPKI
[3-4 sentences. The slope is the cycles lost per misprediction. Compare it
with the pipeline depth of this machine and with the two benchmarks.]

## Graph 6: loss vs width
[3-5 sentences. How does the % of IPC lost change from W=1 to W=8? Relate to
question (d).]

## Question (a): not-taken vs perfect
[Give the IPC loss for both benchmarks. Why is it so large on a 4-wide
out-of-order machine? Hints: many branches are taken (loop branches), each wrong
guess discards the wrong-path instructions fetched meanwhile and restarts fetch,
and a 4-wide machine fetches and discards more instructions per lost cycle.]

## Question (b): bimodal 512 vs 2048
[Give the difference in accuracy and IPC. Explain with aliasing: a bimodal
table is indexed by the branch address, so two branches whose addresses map to
the same entry share one counter and disturb each other. Fewer entries means
more sharing. Which benchmark has more static branches (a bigger code
footprint), and so gains more from a larger table? If the difference is small,
say so and explain why.]

## Question (c): MPKI and the best predictor
[Table of MPKI for all five real predictors. Which is best for each benchmark?
Why can a 2-level predictor with ONE global history register do worse than
bimodal? Hints: the index uses only recent global outcomes and not the branch
address, so different branches with the same history share a counter, and it
learns slowly. How does the combined predictor fix this? A chooser table picks,
per branch, whichever component (bimodal or 2-level) has been more accurate.]

## Question (d): loss of the best real predictor, and why wider/deeper loses more
[Give the IPC loss of the best real predictor vs perfect, from Graph 2. Then use
Graph 6: how the loss grows with W. Hints: a wider machine fetches more
wrong-path instructions per cycle of misprediction penalty, and a deeper
machine has a longer penalty, so each misprediction wastes more slots. Higher
peak IPC means the same number of lost cycles costs more instructions.]

## Observations / problems
- [anything surprising]