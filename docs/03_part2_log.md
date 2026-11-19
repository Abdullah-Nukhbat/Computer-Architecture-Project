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

## Graph 1 and question (a): IPC vs W (data/part2_g1_ipc_vs_width.png)
With out-of-order issue, IPC grows from 0.68 to 2.28 for compress95 (x3.4) and
from 0.51 to 1.03 for cc1 (x2.0) as W goes from 1 to 8. In-order issue barely
moves, from 0.67 to 0.78 and from 0.48 to 0.61. If IPC grew in step with width,
the out-of-order machines would reach 5.4 and 4.1 at W=8, but they only get 42%
and 25% of that. Each doubling helps less than the one before. compress95 gains
79%, then 54%, then 22%, and cc1 gains 43%, 25% and 12%, so both curves flatten
between W=4 and W=8. Functional units are not the limit, since we add an ALU for
every unit of width. What runs out is independent work. Data dependences, a
misprediction every 56 (compress95) or 44 (cc1) instructions and, for cc1, 76
instruction misses per 1000 instructions all leave the issue slots with nothing
to do. The in-order lines are flat almost from the start because in-order issue
stops at the first instruction that is waiting for an operand or a cache miss,
however many slots are free. Extra width only pays off when the core can look
past stalled instructions, and even then only as long as the program has
independent work to give it.

## Graph 2 and question (b): speedup of OoO over in-order (data/part2_g2_speedup.png)
Out-of-order issue makes almost no difference on a 1-wide machine. It speeds
compress95 up by only 1.007x and cc1 by 1.074x. At W=8 the speedup grows to 2.92x
and 1.69x, which means out-of-order issue removes 66% of compress95's in-order
cycles and 41% of cc1's. A 1-wide machine can only issue one instruction per
cycle anyway, so there is little to reorder and not much is lost by waiting in
program order. On an 8-wide machine, one stalled instruction can leave 7 other
slots empty every cycle under in-order issue, while out-of-order issue fills them
with independent instructions from the 64-entry window. compress95 gains much
more because it has more independent instructions for the window to find. cc1's
window is often empty for reasons that reordering cannot fix. Width and
out-of-order issue really need each other to be worth building.

## Graph 3: IPC as % of peak (data/part2_g3_pct_of_peak.png)
Out-of-order compress95 uses 67.7% of its peak IPC at W=1 but only 28.5% at W=8,
and cc1 drops from 51.5% to 12.9%. In-order issue at W=8 uses less than 10% of the
peak for both programs. Per issue slot, going from W=1 to W=2 adds 0.53 IPC for
each extra slot on compress95, while going from W=4 to W=8 adds only 0.10. For
cc1 the drop is from 0.22 to 0.03. Every new slot finds less independent work
than the last one did, because neither program has enough parallelism between
mispredictions and misses to fill 8 slots. Doubling the issue hardware from 4 to
8 bought compress95 22% and cc1 12%, and for cc1 most of that extra width just
sits idle. We would only build the 8-wide machine for programs like compress95,
and it would need a bigger window or a better predictor to keep it fed.

## Graph 4: RUU occupancy (data/part2_g4_ruu_occupancy.png)
With out-of-order issue, compress95 keeps 22 to 31 of the 64 RUU entries busy and
cc1 only 9 to 10, at every width. Dividing occupancy by IPC gives the average
time an instruction spends in the window. At W=8 that is about 14 cycles for
compress95 and 10 for cc1, almost the same as at W=4 (13 and 10). compress95's RUU
is full in 15.3% of cycles at W=8 compared with 3.9% at W=4, so at the widest
setting the window starts to hold it back. cc1's RUU is almost never full, 2.0% of
cycles at most. Its window is empty because instruction misses and
mispredictions stop new instructions from arriving, and a bigger window would not
change that. In-order runs hold only 1.6 to 2.9 entries, since nothing can issue
past a stalled instruction. For compress95 the window size is worth a closer
look, which is what Part 3 does. For cc1 a bigger window would mostly sit empty.

## Question (c): which benchmark has more ILP?
compress95 has clearly more instruction-level parallelism. Its out-of-order IPC
grows x3.4 from W=1 to W=8 against x2.0 for cc1, it reaches 2.28 at W=8 against
1.03, and out-of-order issue speeds it up 2.92x against 1.69x. It also keeps about
three times as many instructions in the window (31.5 entries against 10.2 at
W=8), which shows the core finds far more independent instructions to overlap.

## Observations / problems
- The W=4 out-of-order runs use the same configuration as the Part 3 RUU 64 runs
  and give exactly the same IPC (1.8629 and 0.9222).
