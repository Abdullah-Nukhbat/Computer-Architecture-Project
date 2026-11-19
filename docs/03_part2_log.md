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
| Benchmark | W | IPC out-of-order | IPC in-order | Speedup (cycles in-order / out-of-order) | OoO % of peak | OoO RUU occupancy | OoO RUU full |
|---|---|---|---|---|---|---|---|
| compress95 | 1 | 0.6770 | 0.6724 | 1.007 | 67.7% | 22.0 | 3.3% |
| compress95 | 2 | 1.2092 | 0.7515 | 1.609 | 60.5% | 22.4 | 2.3% |
| compress95 | 4 | 1.8629 | 0.7792 | 2.391 | 46.6% | 24.2 | 3.9% |
| compress95 | 8 | 2.2794 | 0.7797 | 2.923 | 28.5% | 31.5 | 15.3% |
| cc1 | 1 | 0.5148 | 0.4795 | 1.074 | 51.5% | 10.3 | 1.4% |
| cc1 | 2 | 0.7360 | 0.5374 | 1.370 | 36.8% | 9.3 | 0.8% |
| cc1 | 4 | 0.9222 | 0.5854 | 1.575 | 23.1% | 9.2 | 0.9% |
| cc1 | 8 | 1.0320 | 0.6109 | 1.689 | 12.9% | 10.2 | 2.0% |

## Graph 1: IPC vs W (data/part2_g1_ipc_vs_width.png)
With out-of-order issue, IPC rises from 0.68 at W=1 to 2.28 at W=8 for
compress95 (x3.37) and from 0.51 to 1.03 for cc1 (x2.00), while in-order issue
barely moves: 0.67 to 0.78 (x1.16) and 0.48 to 0.61 (x1.27). Doubling W never
doubles IPC: each doubling gives compress95 +79%, +54% and then only +22%, and
cc1 +43%, +25% and +12%, so both curves flatten between W=4 and W=8. The in-order
curves are flat almost from the start because in-order issue stops at the first
instruction whose operands are not ready, so data dependences and every cache
miss block all younger instructions however wide the machine is. Out-of-order
issue removes that limit, and what remains is branches and cache misses:
compress95 mispredicts once every 56 instructions (18.0 MPKI) and cc1 once every
44 (22.6 MPKI), and a 64-entry window can never hold much more useful work than
that before a misprediction throws it away. cc1 flattens lower because its
instruction-cache misses (76 per 1000 instructions) also starve the front end.
Functional units are not the limit, because their number grows with W.

## Graph 2: speedup of OoO over in-order (data/part2_g2_speedup.png)
At W=1, out-of-order issue is almost useless: it runs only 1.007x faster than
in-order on compress95 and 1.074x on cc1. At W=8 the speedup grows to 2.92x for
compress95 and 1.69x for cc1. This answers question (b): a 1-wide machine can
issue only one instruction per cycle anyway, so there is little room to reorder,
and an in-order 1-wide pipeline loses little by waiting. A wide machine has many
issue slots every cycle; in-order issue leaves them empty as soon as one
instruction stalls, while out-of-order issue fills them with independent younger
instructions from the 64-entry window. The more slots there are, the more an
in-order machine wastes, so the gain from out-of-order issue grows with W.

## Graph 3: IPC as % of peak (data/part2_g3_pct_of_peak.png)
Out-of-order compress95 uses 67.7% of the peak at W=1 but only 28.5% at W=8;
cc1 falls from 51.5% to 12.9%. In-order issue at W=8 uses only 9.7% and 7.6% of
the peak. Each extra unit of width is used less than the one before, which is
diminishing returns: the program does not have enough independent instructions
between mispredictions and misses to fill 8 slots per cycle. Doubling W from 4
to 8 costs twice the issue hardware for +22% (compress95) or +12% (cc1).

## Graph 4: RUU occupancy (data/part2_g4_ruu_occupancy.png)
With out-of-order issue, compress95 keeps 22 to 31 of the 64 RUU entries busy on
average, and the RUU is full in 15.3% of cycles at W=8 (against 3.9% at W=4), so
at W=8 the window starts to become a limit for compress95. cc1 uses only 9 to 10
entries at every width and the RUU is almost never full (at most 2.0% of cycles):
its window is empty because instruction-cache misses and mispredictions stop
new instructions from arriving, not because 64 entries is too small. In-order
runs use only 1.6 to 2.9 entries, since instructions issue in order and cannot pile
up behind a stalled one. For cc1 the window is not the limit; for compress95 it
starts to be at W=8, which Part 3 explores.

## Question (c): which benchmark has more ILP?
compress95 has more instruction-level parallelism. Its out-of-order IPC grows
x3.37 from W=1 to W=8 against x2.00 for cc1, it reaches IPC 2.28 at W=8 against
1.03, and out-of-order issue speeds it up 2.92x against 1.69x. It also keeps
three times as many instructions in the RUU (31.5 against 10.2 at W=8), which
shows the window finds many more independent instructions to overlap.

## Observations / problems
- The W=4 out-of-order runs use the same configuration as the Part 3 RUU 64 runs
  and give the same IPC (1.8629 and 0.9222), which confirms the runs are
  repeatable.
