# Part 6 log: Design your own processor

## Setup
- Designs and cost model: scripts/p6_designs.py (one place, used by both scripts)
- Runs: scripts/run_P6.sh (every design within budget, both benchmarks,
  -max:inst 100000000); designs over 100 units are refused and never run
- Graphs and table: scripts/part6_graphs.py
- Final configuration file: configs/P6_final.cfg (made with -dumpconfig)
- Raw outputs: results/*_P6_*.txt
- Data: data/part6_candidates.csv
- Performance = geometric mean of IPC = sqrt(IPC_compress95 x IPC_cc1)
- Check: the cost model gives 86 units for the default configuration, as in the
  project statement; re-running both benchmarks with
  `-config configs/P6_final.cfg` reproduces the D24 IPC exactly (2.1953, 1.2488).

## (a) Final design: D24

Run it with:

    env -i ./sim-outorder -config P6_final.cfg -redir:sim compress95_P6_final.txt ../Programs/compress95.ss < compress95.in > compress95.out
    env -i ./sim-outorder -config P6_final.cfg -redir:sim cc1_P6_final.txt ../Programs/cc1.ss -O 1stmt.i

Options that differ from the default:

    -fetch:ifqsize 8 -decode:width 8 -issue:width 8 -commit:width 8
    -res:ialu 8 -res:memport 4 -ruu:size 64 -lsq:size 32
    -cache:il1 il1:32:64:8:l -cache:dl1 dl1:32:32:8:l
    -cache:dl2 ul2:128:64:16:l -cache:il2 dl2 -bpred comb

Cost, line by line:

| Component | Setting | Rule | Cost |
|---|---|---|---|
| Width | W = 8 (memport 4) | 4 x W | 32 |
| RUU | 64 entries (LSQ 32) | 0.25 x 64 | 16 |
| L1 I-cache | il1:32:64:8:l = 32 x 64 B x 8 = 16 KB | 1 per KB | 16 |
| L1 D-cache | dl1:32:32:8:l = 32 x 32 B x 8 = 8 KB | 1 per KB | 8 |
| L2 (unified) | ul2:128:64:16:l = 128 x 64 B x 16 = 128 KB | 0.125 per KB | 16 |
| Branch predictor | comb (default sizes) | fixed | 6 |
| Issue | out-of-order | free | 0 |
| **Total** | | | **94 / 100** |

Default configuration for comparison: 16 + 4 + 16 + 16 + 32 + 2 = 86.

| | Default (86 units) | D24 (94 units) | Change |
|---|---|---|---|
| IPC compress95 | 1.7145 | 2.1953 | +28.0% |
| IPC cc1 | 0.8849 | 1.2488 | +41.1% |
| Geometric mean | 1.2317 | 1.6557 | +34.4% |

## (b) The path: every candidate simulated (26 designs)
Stage 1 (D00-D06) changes one idea at a time from the default. Stage 2 (D07-D15)
combines the winners and tests where to take units from. Stage 3 (D16-D21) merges
the two best and tries the free knobs (associativity, block size). Stage 4
(D22-D25) refines around the leader.

| Design | Configuration | Cost | IPC compress95 | IPC cc1 | Geo. mean | vs default |
|---|---|---|---|---|---|---|
| D00 | W=4, RUU 16, il1 16 KB 1-way 32 B, dl1 16 KB 4-way 32 B, L2 256 KB 4-way 64 B, bimod 2048 | 86 | 1.7145 | 0.8849 | 1.2317 | +0.0% |
| D01 | W=4, RUU 16, il1 16 KB 1-way 32 B, dl1 16 KB 4-way 32 B, L2 256 KB 4-way 64 B, comb | 90 | 1.8442 | 0.9003 | 1.2885 | +4.6% |
| D02 | W=4, RUU 64, il1 16 KB 1-way 32 B, dl1 16 KB 4-way 32 B, L2 256 KB 4-way 64 B, bimod 2048 | 98 | 1.8629 | 0.9222 | 1.3107 | +6.4% |
| D03 | W=4, RUU 16, il1 16 KB 4-way 32 B, dl1 16 KB 4-way 32 B, L2 256 KB 4-way 64 B, bimod 2048 | 86 | 1.7185 | 0.9516 | 1.2788 | +3.8% |
| D04 | W=8, RUU 32, il1 16 KB 1-way 32 B, dl1 16 KB 4-way 32 B, L2 128 KB 4-way 64 B, bimod 2048 | 90 | 2.0401 | 0.9659 | 1.4038 | +14.0% |
| D05 | W=4, RUU 32, il1 16 KB 1-way 32 B, dl1 16 KB 4-way 32 B, L2 256 KB 4-way 64 B, comb | 94 | 1.9172 | 0.9307 | 1.3358 | +8.5% |
| D06 | W=4, RUU 64, il1 32 KB 4-way 32 B, dl1 16 KB 4-way 32 B, no L2, comb | 86 | 1.6121 | 0.7526 | 1.1015 | -10.6% |
| D07 | W=8, RUU 32, il1 16 KB 4-way 32 B, dl1 16 KB 4-way 32 B, L2 128 KB 4-way 64 B, comb | 94 | 2.1002 | 1.0570 | 1.4899 | +21.0% |
| D08 | W=8, RUU 64, il1 16 KB 4-way 32 B, dl1 16 KB 4-way 32 B, L2 64 KB 4-way 64 B, comb | 94 | 1.9909 | 0.9217 | 1.3546 | +10.0% |
| D09 | W=8, RUU 64, il1 16 KB 4-way 32 B, dl1 8 KB 4-way 32 B, L2 128 KB 4-way 64 B, comb | 94 | 2.1733 | 1.0600 | 1.5178 | +23.2% |
| D10 | W=8, RUU 32, il1 16 KB 8-way 32 B, dl1 16 KB 8-way 32 B, L2 128 KB 8-way 64 B, comb | 94 | 2.1201 | 1.0880 | 1.5188 | +23.3% |
| D11 | W=8, RUU 32, il1 32 KB 4-way 32 B, dl1 8 KB 4-way 32 B, L2 64 KB 4-way 64 B, comb | 94 | 1.8637 | 1.0320 | 1.3868 | +12.6% |
| D12 | W=8, RUU 64, il1 16 KB 4-way 32 B, dl1 16 KB 4-way 32 B, L2 128 KB 4-way 64 B, bimod 2048 | 98 | 2.1155 | 1.0618 | 1.4987 | +21.7% |
| D13 | W=8, RUU 32, il1 16 KB 4-way 32 B, dl1 16 KB 4-way 32 B, L2 128 KB 4-way 64 B, bimod 8192 | 96 | 2.0460 | 1.0585 | 1.4716 | +19.5% |
| D14 | W=4, RUU 64, il1 16 KB 4-way 32 B, dl1 16 KB 4-way 32 B, L2 256 KB 4-way 64 B, bimod 2048 | 98 | 1.8678 | 0.9975 | 1.3650 | +10.8% |
| D15 | W=8, RUU 64, il1 16 KB 4-way 32 B, dl1 16 KB 4-way 32 B, L2 32 KB 4-way 64 B, comb | 90 | 1.8186 | 0.7037 | 1.1313 | -8.2% |
| D16 | W=8, RUU 64, il1 16 KB 8-way 32 B, dl1 8 KB 8-way 32 B, L2 128 KB 8-way 64 B, comb | 94 | 2.1904 | 1.0949 | 1.5486 | +25.7% |
| D17 | W=8, RUU 64, il1 16 KB 8-way 64 B, dl1 8 KB 8-way 32 B, L2 128 KB 8-way 64 B, comb | 94 | 2.1905 | 1.2391 | 1.6475 | +33.8% |
| D18 | W=8, RUU 64, il1 16 KB 8-way 64 B, dl1 8 KB 8-way 64 B, L2 128 KB 8-way 64 B, comb | 94 | 2.1892 | 1.2389 | 1.6469 | +33.7% |
| D19 | W=8, RUU 64, il1 16 KB 16-way 32 B, dl1 8 KB 16-way 32 B, L2 128 KB 16-way 64 B, comb | 94 | 2.1997 | 1.1030 | 1.5576 | +26.5% |
| D20 | W=8, RUU 64, il1 16 KB 8-way 32 B, dl1 8 KB 8-way 32 B, L2 128 KB 8-way 64 B, bimod 4096 | 92 | 2.0879 | 1.0905 | 1.5089 | +22.5% |
| D21 | W=8, RUU 64, il1 16 KB 8-way 64 B, dl1 8 KB 8-way 32 B, L2 128 KB 8-way 64 B, bimod 8192 | 96 | 2.0877 | 1.2426 | 1.6106 | +30.8% |
| D22 | W=8, RUU 64, il1 16 KB 8-way 128 B, dl1 8 KB 8-way 32 B, L2 128 KB 8-way 128 B, comb | 94 | 2.0360 | 1.2887 | 1.6198 | +31.5% |
| D23 | W=8, RUU 64, il1 16 KB 16-way 64 B, dl1 8 KB 8-way 32 B, L2 128 KB 8-way 64 B, comb | 94 | 2.1902 | 1.2390 | 1.6473 | +33.7% |
| D24 | W=8, RUU 64, il1 16 KB 8-way 64 B, dl1 8 KB 8-way 32 B, L2 128 KB 16-way 64 B, comb | 94 | 2.1953 | 1.2488 | 1.6557 | +34.4% |
| D25 | W=8, RUU 32, il1 16 KB 8-way 64 B, dl1 16 KB 8-way 32 B, L2 128 KB 8-way 64 B, comb | 94 | 2.1197 | 1.2304 | 1.6150 | +31.1% |

### Graph 1: geometric-mean IPC vs cost (data/part6_g1_ipc_vs_cost.png)
The scatter plot shows all 26 designs we simulated, costing from 86 to 98 units.
Their geometric-mean IPC ranges from 1.10, for the design with no L2, to 1.66 for
our final design D24, against 1.23 for the default configuration. Cost on its own
predicts very little: most of the best designs cost exactly 94 units, but so do
some of the weaker ones, such as D05 (1.34) and D08 (1.35). What matters is where
the units go. The best designs all spend 32 units on an 8-wide core, keep a 128 KB
L2 and use the free options, associativity and block size, to cut cc1's
instruction misses, while the worst ones shrink or remove the L2. Under a fixed
budget, putting the units where each program is actually limited beats simply
spending more of them.

### Graph 2: final design vs default (data/part6_g2_final_vs_default.png)
Our final design raises IPC from 1.715 to 2.195 on compress95 (28%) and from 0.885
to 1.249 on cc1 (41%), for 94 units against the default's 86. The two programs
gain for different reasons. compress95 profits from the wider core and bigger
window: its average RUU occupancy grows from 12.4 to 37.0 entries, and its
mispredictions fall from 18.0 to 15.4 per 1000 instructions with the combined
predictor, even though the smaller 8 KB data cache now misses 6.1% of accesses
instead of 4.7%. cc1 profits mainly from the instruction cache: 8-way
associativity and 64-byte blocks cut its instruction misses from 80.8 to 42.1 per
1000 instructions, so the wider core is finally fed. cc1 gains more in
percentage because instruction misses were its main bottleneck, and under this
cost model they were almost free to fix.

## (c) Justification
Our design spends the budget where Parts 2 to 5 showed our two programs lose the
most: issue width and window for compress95, and the instruction supply for
cc1. It reaches a geometric-mean IPC of 1.656 for 94 units, 34% above the
default configuration's 1.232 at 86 units.

Width and window (48 of 94 units). Part 2 showed that compress95 has a lot of
ILP: its out-of-order IPC was still rising at W=8 (1.86 to 2.28), and in Part 3(c)
a W=8 machine beat a W=4 machine with a four-times-larger window. In the search,
moving to W=8 with a 32-entry RUU (D04) was the largest single step, +14%, even
though we paid for it by halving the L2. At W=8, however, a 16- or 32-entry RUU is
too small to keep 8 issue slots busy, so we doubled the RUU to 64. To pay for it
we cut the L1 data cache from 16 KB to 8 KB, and this trade won both times we
tried it (D16 against D10, D17 against D25). The larger window hides most of the
extra data misses, which Part 4 showed cost only 6 cycles each when they hit in
the L2.

Branch predictor (6 units). Part 5 showed the combined predictor is the most
accurate for both programs (12.4 and 20.2 MPKI) and that mispredictions cost an
aggressive core more. On its own it gave +4.6% over the default for 4 extra units
(D01). A larger bimodal table is not a substitute: bimod 8192 costs more (8
units) and lost to the combined predictor (D21: 1.611 against D17: 1.648).

Instruction cache (16 units, same size as the default). Part 4(d) showed that
cc1's main problem is instruction misses: 80.8 per 1000 instructions. Instead of
paying for a bigger cache, we used the options the cost model gives for free.
Making the 16 KB instruction cache 4-way instead of direct-mapped raised cc1's IPC
by 7.5% on its own (D03), and 64-byte blocks raised it by another 13.2% (1.095 to
1.239, D16 to D17), because a compiler's code runs through long sequences of
instructions, so each 64-byte block brings in the next 8 instructions (PISA
instructions are 8 bytes) before they are needed. Making the 128 KB L2 16-way
(D24) added a final 0.5%.

What we gave up. The L1 data cache is half the default size (8 KB) and the L2 is
half the default size (128 KB). The L2 cannot go lower: Part 4(c) showed it is
what protects cc1 from memory latency, and in the search a 64 KB L2 (D08) cut cc1
to 0.922 and a 32 KB L2 (D15) to 0.704, while removing it (D06) gave the worst
design of all (-10.6%). We also tried 128-byte instruction blocks (D22), which
helped cc1 (1.289) but hurt compress95 (2.036), lowering the mean. 6 units are
left unused, because nothing that would still help costs 6 units or less: the next
RUU size (128) costs 16 more and returning the data cache to 16 KB costs 8 more.

Our design relies on two simplifications in the simulator. Cache associativity
and block size are free in the cost model, and sim-outorder keeps an L1 hit at 1
cycle however associative the cache is. Real 8- and 16-way caches would be slower
and use more power, so part of our gain from them would shrink in real hardware.
Within the rules of this project, though, D24 is the fastest design we found,
and it is faster on both benchmarks individually: +28.0% for compress95 and +41.1%
for cc1.

## Observations / problems
- The default configuration simulated in Part 6 (D00) gives exactly the Part 3
  RUU 16 results (compress95 1.7145, cc1 0.8849), which confirms the cost-model
  baseline.
