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

Scatter plot: data/part6_g1_ipc_vs_cost.png. Final vs default: data/part6_g2_final_vs_default.png.

## (c) Justification (half to one page)
[Your own words. Points backed by the results:
- Width: Part 2 showed compress95 keeps gaining up to W=8 (OoO IPC 1.86 -> 2.28),
  and in Part 3(c) W=8/RUU16 beat W=4/RUU64. D04 (W=8) was the biggest
  single step: +14%. Width costs 4 per W, so W=8 is a third of the budget.
- RUU 64: Part 3 showed gains flatten after 32-64 entries at W=4; at W=8 the
  window must be bigger to keep 8 units busy. Trading the dl1 from 16 KB down to
  8 KB to pay for RUU 32 -> 64 won both times it was tried (D16 1.549 vs D10
  1.519; D17 1.648 vs D25 1.615).
- Combined predictor: Part 5, best on both (MPKI 12.4 and 20.2); 6 units for
  +4.6% on its own (D01). Bimodal 8192 (D21, 8 units) did worse than comb.
- Instruction cache: cc1's biggest problem is il1 misses (Part 4(d): 80.8 per
  1000 instructions). Associativity and block size are free in the cost model:
  4-way il1 alone gave cc1 +7.5% (D03); 64 B blocks lifted cc1 from 1.09 to
  1.24 (D16 -> D17) because compiler code is long straight-line sequences.
- What we gave up: dl1 is halved to 8 KB (the bigger RUU hides the extra data
  misses, see above) and L2 to
  128 KB. L2 can't go lower: 64 KB (D08) and 32 KB (D15) badly hurt cc1, which
  matches Part 4(c,d). No L2 at all (D06) was the worst design (-10.6%).
- 6 units are left unused: nothing useful costs 6 or less (RUU 128 would cost
  +16, a 16 KB dl1 +8).
- Caveat: the simulator keeps hit latency at 1 cycle whatever the
  associativity, so the free 8/16-way caches would be slower in real hardware.]

## Observations / problems
- [anything surprising]
