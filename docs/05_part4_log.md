# Part 4 log: Memory hierarchy

## Setup
- Script: scripts/run_P4.sh (32 runs), graphs: scripts/part4_graphs.py
- All runs: default configuration + -max:inst 100000000, only the options below change
- (a) -cache:dl1 dl1:8:32:4:l | dl1:32:32:4:l | dl1:128:32:4:l | dl1:512:32:4:l  (1/4/16/64 KB)
- (b) -cache:dl1 dl1:512:8:4:l | dl1:256:16:4:l | dl1:128:32:4:l | dl1:64:64:4:l  (8/16/32/64 B blocks)
- (c) -mem:lat 25 2 | 50 2 | 100 2 | 200 2, with the default L2 and again with
  -cache:dl2 none -cache:il2 none
- Extra runs for question (a), scripts/run_P4_3c.sh (10 runs): a fully-associative
  dl1 of each size (dl1:1:32:<ways>:l) and a 4 MB dl1 (dl1:32768:32:4:l)
- Raw outputs: results/*_P4a_*, *_P4b_*, *_P4c_*, *_P4x_*
- Data: data/part4_table.csv, data/part4c_slopes.csv, data/part4a_3c.csv
- Check: the 16 KB and 32 B runs are the default configuration and match Part 3
  RUU 16 (compress95 IPC 1.7145, cc1 0.8849).

## Results

(a) L1 data-cache capacity

| Capacity | compress95 dl1 miss | compress95 IPC | cc1 dl1 miss | cc1 IPC |
|---|---|---|---|---|
| 1 KB | 9.45% | 1.6009 | 11.41% | 0.8368 |
| 4 KB | 6.99% | 1.6547 | 4.32% | 0.8683 |
| 16 KB (default) | 4.70% | 1.7145 | 1.42% | 0.8849 |
| 64 KB | 2.68% | 1.7753 | 0.35% | 0.8976 |

(b) L1 data-cache block size (16 KB)

| Block | compress95 dl1 miss | compress95 IPC | cc1 dl1 miss | cc1 IPC |
|---|---|---|---|---|
| 8 B | 7.79% | 1.7014 | 2.41% | 0.8818 |
| 16 B | 5.69% | 1.7104 | 1.78% | 0.8839 |
| 32 B (default) | 4.70% | 1.7145 | 1.42% | 0.8849 |
| 64 B | 4.31% | 1.7144 | 1.28% | 0.8854 |

(c) CPI vs memory latency (CPI per +100 cycles = least-squares slope)

| | lat 25 | lat 50 | lat 100 | lat 200 | CPI per +100 cycles |
|---|---|---|---|---|---|
| compress95, with L2 | 0.588 | 0.605 | 0.639 | 0.707 | 0.068 |
| compress95, no L2 | 0.784 | 1.003 | 1.441 | 2.317 | 0.876 |
| cc1, with L2 | 1.155 | 1.247 | 1.432 | 1.805 | 0.371 |
| cc1, no L2 | 2.978 | 4.939 | 8.864 | 16.717 | 7.851 |

(a) 3C split of dl1 misses (% of data accesses)

| | 1 KB | 4 KB | 16 KB | 64 KB |
|---|---|---|---|---|
| compress95 compulsory | 0.068 | 0.068 | 0.068 | 0.068 |
| compress95 capacity | 8.846 | 6.606 | 4.326 | 2.501 |
| compress95 conflict | 0.538 | 0.313 | 0.307 | 0.108 |
| cc1 compulsory | 0.054 | 0.054 | 0.055 | 0.055 |
| cc1 capacity | 10.532 | 3.732 | 1.220 | 0.229 |
| cc1 conflict | 0.828 | 0.536 | 0.148 | 0.065 |

How: compulsory = misses of a 4 MB cache (nothing is ever evicted); capacity =
misses of a fully-associative cache of the same size minus compulsory; conflict =
misses of the real 4-way cache minus the fully-associative one.

## Graph 1a: dl1 miss rate vs capacity (data/part4_g1_dl1_miss_vs_capacity.png)
[4-6 sentences. compress95 9.45% -> 2.68%, cc1 11.41% -> 0.35%. cc1's data fits
almost entirely by 16 KB; compress95's hash table still does not fit at 64 KB.]

## Graph 1b: IPC vs capacity (data/part4_g2_ipc_vs_capacity.png)
[4-6 sentences. compress95 1.601 -> 1.775 (+10.9%), cc1 0.837 -> 0.898 (+7.3%).
Explain why a large drop in miss rate gives a small IPC change: L2 catches the
misses (hit in 6 cycles), and the out-of-order core hides part of that.]

## Graph 2a/2b: block size (data/part4_g3_dl1_miss_vs_block.png, part4_g4_ipc_vs_block.png)
[4-6 sentences each. Miss rate falls every time the block doubles (spatial
locality), but the drop shrinks (32 -> 64 B: -0.39 points compress95, -0.14 cc1).
IPC barely moves: compress95 is highest at 32 B (1.7145), not at 64 B (1.7144).]

## Graph 3: CPI vs memory latency (data/part4_g5_cpi_vs_latency.png)
[4-6 sentences. Use the slope table. Note the y-axis is log scale.]

## Graph 4 (extra): 3C breakdown (data/part4_g6_3c_breakdown.png)
## Graph 5 (extra): L1 misses per 1000 instructions (data/part4_g7_l1_misses_per_1000.png)

## Question (a): classify the misses (3 Cs), explain the capacity graph
[Capacity misses are almost all of it for both programs; compulsory are tiny
(~0.06% of accesses: 100M instructions touch each block once but reuse it many
times); conflict misses are small with 4-way and shrink as size grows. So
growing the cache removes capacity misses, which is why the miss-rate curve
keeps falling. cc1's working set fits by 16 KB (capacity 1.2%); compress95's
does not (capacity 2.5% even at 64 KB).]

## Question (b): block size, spatial locality, miss penalty; lowest miss rate = highest IPC?
[Bigger blocks bring in neighbours that are used soon (spatial locality), so miss
rate falls. But each miss moves more bytes (longer penalty) and there are fewer
blocks to hold different data. compress95: 64 B has the lowest miss rate but 32 B
has the highest IPC, so no. cc1: 64 B is best on both, by a tiny margin.]

## Question (c): CPI per extra 100 cycles, with and without L2; value of an L2
[With L2: +0.068 (compress95) and +0.371 (cc1) CPI per 100 cycles. Without L2:
+0.876 and +7.851, i.e. 13x and 21x more. The L2 filters out most L1 misses
(ul2 miss rate 9.9% and 4.2% in Part 1), so only a few ever see main-memory
latency. An L2 makes the machine nearly insensitive to memory speed.]

## Question (d): which misses cause the damage without L2?
[Use Graph 5: cc1 has 80.8 il1 misses per 1000 instructions vs 5.9 dl1; compress95
has 0.16 il1 vs 17.4 dl1. cc1 is destroyed by INSTRUCTION misses: with no L2,
every il1 miss waits for memory and the front end stops fetching, which the
out-of-order core cannot hide (nothing to execute). compress95 suffers from
DATA misses, which the RUU can partly overlap, so it degrades far less.]

## Question (e): were the Part 1 predictions right?
[Part 1 expected compress95 to be more sensitive to the L1 data cache and cc1 to
the instruction side. Results: dl1 capacity changes compress95's IPC more (+10.9%
vs +7.3%); removing L2 hurts cc1 far more (CPI x9.3 at lat 200 vs x3.3). Say
whether this matches your prediction.]

## Observations / problems
- [anything surprising]
