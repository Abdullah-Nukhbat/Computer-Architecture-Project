# Part 2 log: Width and in-order vs out-of-order

## Setup
- Script: scripts/run_P2.sh (16 runs), graphs: scripts/part2_graphs.py
- Fixed for all runs: -max:inst 100000000 -ruu:size 64 -lsq:size 32
- Width W sets: -fetch:ifqsize -decode:width -issue:width -commit:width -res:ialu
- -res:memport = 1, 1, 2, 4 for W = 1, 2, 4, 8
- In-order runs add: -issue:inorder true
- Raw outputs: results/*_P2_W*_{ooo,inorder}.txt
- Data: data/part2_table.csv

## Results table
[paste the table printed by part2_graphs.py]

## Graph 1: IPC vs W
[4-6 sentences. Start with numbers (IPC at W=1 and W=8 for each line, and the
percentage change). Then explain why. Answer question (a): does IPC double when
W doubles? Where do the curves flatten, and what limits them (data dependences,
branches, cache misses, functional units)? Use your Part 1 numbers: compress95
dl1 miss 4.7%, cc1 il1 miss 5.8%, MPKI 18.0 and 22.6.]

## Graph 2: speedup of OoO over in-order
[4-6 sentences. Give the speedup at W=1 and W=8. Answer question (b): why does
out-of-order gain more at large W than at W=1? Hint: at W=1 only one
instruction issues per cycle, so there is little to reorder. A wide machine has
many free slots that out-of-order can fill with independent instructions
instead of stalling behind a dependent or missing one.]

## Graph 3: IPC as % of peak
[3-4 sentences. State the % of peak at W=8 versus W=1 and what that says about
diminishing returns.]

## Graph 4: RUU occupancy
[3-4 sentences. Compare occupancy to the 64-entry window. If occupancy stays
low, the window is not the limit.]

## Question (c): which benchmark has more ILP?
[2-3 sentences. Support with numbers: the benchmark whose IPC keeps rising with
W, and whose out-of-order speedup is larger, has more ILP.]

## Observations / problems
- [anything surprising]