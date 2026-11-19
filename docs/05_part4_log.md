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

How we split them. Compulsory misses are the misses of a 4 MB cache, where
nothing is ever evicted. Capacity misses are the misses of a fully-associative
cache of the same size, minus the compulsory ones. Conflict misses are the misses
of the real 4-way cache minus those of the fully-associative one.

## Graph 1a: dl1 miss rate vs capacity (data/part4_g1_dl1_miss_vs_capacity.png)
Growing the L1 data cache from 1 KB to 64 KB lowers compress95's miss rate from
9.45% to 2.68% and cc1's from 11.41% to 0.35%. Counted per 1000 instructions,
compress95 goes from 35.0 misses to 9.9 and cc1 from 47.7 to just 1.4. cc1 starts
worse but improves much faster. By 16 KB it misses only 1.42% of accesses, while
compress95 loses just 26% to 43% of its misses with each 4x step. Graph 4 shows
that nearly all of these misses are capacity misses, so this curve is really a
picture of each program's working set. Most of cc1's data fits in about 16 KB.
compress95's hash table is bigger than 64 KB and is read at scattered positions.
At the sizes anyone would actually build, a bigger data cache is worth far more
to compress95 than to cc1.

## Graph 1b: IPC vs capacity (data/part4_g2_ipc_vs_capacity.png)
IPC rises from 1.601 to 1.775 for compress95 (11%) and from 0.837 to 0.898 for cc1
(7%) as the data cache grows from 1 KB to 64 KB. That is much less than the drop
in misses would suggest. Going from 1 KB to 64 KB removes 25 misses per 1000
instructions for compress95 and 46 for cc1. If each of those had cost the full
6-cycle L2 hit time, CPI would fall by about 0.15 and 0.28, but the measured falls
are only 0.061 and 0.081. Each miss really cost about 2.4 cycles for compress95
and 1.7 for cc1, which means the out-of-order core hid roughly 60% and 70% of the
L2 latency by running other instructions in the meantime. cc1 saves more CPI but
gains less IPC. Its base CPI (1.13 at 16 KB) is twice compress95's (0.58), and the
same saving is a smaller share of its run time. With an L2 behind it and an
out-of-order core in front of it, a bigger L1 helps, but only modestly.

## Graph 2a: dl1 miss rate vs block size (data/part4_g3_dl1_miss_vs_block.png)
With the capacity fixed at 16 KB, longer blocks cut compress95's miss rate from
7.79% to 4.31% and cc1's from 2.41% to 1.28% between 8 and 64 bytes, about 45% for
both. Each doubling helps less than the last. Going from 8 to 16 bytes removes
2.10 points for compress95, but going from 32 to 64 removes only 0.39. A miss
brings in the whole block, and programs usually touch nearby words soon after
(spatial locality), so a longer block turns some future misses into hits. With
the capacity fixed, though, longer blocks also mean fewer of them, only 256 at 64
bytes compared with 2048 at 8 bytes, and data that is used on its own gets pushed
out sooner. compress95's hash-table accesses are spread out, and it still misses
4.3% of the time even with 64-byte blocks.

## Graph 2b: IPC vs block size (data/part4_g4_ipc_vs_block.png)
IPC barely changes with block size. compress95 goes from 1.7014 at 8 bytes to
1.7145 at 32 bytes (0.8%), and cc1 from 0.8818 to 0.8854 at 64 bytes (0.4%). For
compress95, going from 8 to 64 bytes removes 12.9 misses per 1000 instructions but
saves only 0.004 CPI, about 0.3 cycles per miss, so those misses were almost free
in the first place. The misses that longer blocks remove are neighbouring words
of data that was just loaded, and the out-of-order core overlaps them easily. The
scattered misses that really slow compress95 down are not helped at all. In
sim-outorder, an L1 miss that hits in the L2 costs the same 6 cycles whatever the
block size, so these runs leave out the longer transfer time of a bigger block.
In real hardware that extra time would make 64-byte blocks lose to 32-byte ones,
and 32 bytes is a sensible default.

## Graph 3: CPI vs memory latency (data/part4_g5_cpi_vs_latency.png)
With the L2 in place, raising memory latency from 25 to 200 cycles moves CPI only
from 0.59 to 0.71 for compress95 and from 1.16 to 1.81 for cc1. Without the L2,
CPI rises from 0.78 to 2.32 for compress95 and from 2.98 to 16.7 for cc1. The lines
are almost straight, meaning each extra cycle of latency costs a fixed amount. It
works out to 0.068 and 0.371 CPI per 100 cycles with the L2, and 0.876 and 7.85
without it. With the L2, compress95 sends 2.6 accesses per 1000 instructions to
memory, which would cost 0.26 CPI per 100 cycles if nothing were hidden. It only
pays 0.068, so about three quarters of the latency is hidden. cc1 sends 4.3,
worth 0.43 CPI, and pays 0.37, so only 14% is hidden. Most of cc1's memory traffic
is instruction fetches, and nothing can run while fetch is waiting. Memory
latency hurts most when it delays instructions instead of data. (The y-axis uses
a log scale so that all four lines fit on one graph.)

## Graph 4: 3C breakdown of dl1 misses (data/part4_g6_3c_breakdown.png)
Almost all data-cache misses are capacity misses for both programs. At the
default 16 KB, compress95's 4.70% miss rate splits into 0.07 points compulsory,
4.33 capacity and 0.31 conflict, and cc1's 1.42% into 0.06, 1.22 and 0.15.
Compulsory misses are tiny because over 100 million instructions each block is
reused many times after it is first loaded. Conflict misses are small with 4-way
associativity and shrink as the cache grows, from 0.54 to 0.11 points for
compress95 and from 0.83 to 0.07 for cc1. Capacity misses fall from 8.8% to 2.5%
for compress95 and from 10.5% to 0.23% for cc1 between 1 KB and 64 KB. Since the
misses come from capacity, more associativity would not help much and a bigger
cache would. compress95 needs more than 64 KB, while 16 KB is already enough for
cc1.

## Graph 5: L1 misses per 1000 instructions (data/part4_g7_l1_misses_per_1000.png)
With the default caches, compress95 has 0.16 instruction misses and 17.4 data
misses per 1000 instructions. cc1 is the other way round, with 80.8 instruction
misses and 5.9 data misses. In total cc1 makes 87 L1 misses per 1000 instructions,
five times compress95's 17.6, and without an L2 every one of them goes to main
memory. At 200 cycles of latency, cc1's misses alone would add 17.3 cycles per
instruction if none of the latency were hidden. Its measured CPI is 16.7, so
almost nothing is hidden. compress95's misses would add 3.5 cycles, but its
measured CPI is only 2.3, because data misses can overlap with other work in the
window. The type of miss matters as much as how many there are. Instruction
misses are nearly impossible to hide, and a program with a large code footprint
is the one that needs an L2 the most.

## Question (a): classify the misses (3 Cs), explain the capacity graph
The extra runs let us split every miss into the 3 Cs (Graph 4). Compulsory misses
are tiny and constant, 0.068% of data accesses for compress95 and 0.055% for cc1
at every size, because each block is loaded for the first time once and then
reused many times. Conflict misses are small with a 4-way cache and shrink as the
cache grows. Almost everything else is capacity misses. At 16 KB they make up
4.33 of compress95's 4.70 points and 1.22 of cc1's 1.42. The capacity graph is
therefore mostly the curve of capacity misses, and it falls each time more of
the working set fits. cc1's capacity misses drop from 10.5% to 0.23% because its
data fits by 16 to 64 KB. compress95 still has 2.5% capacity misses at 64 KB
because its hash table is bigger than that.

## Question (b): block size, spatial locality, miss penalty; lowest miss rate = highest IPC?
Spatial locality explains why the miss rate falls with longer blocks. A miss on
one word also brings in the words around it, and the next accesses often land
there. With a fixed 16 KB, though, longer blocks mean fewer of them, and each
doubling helps less (2.10 points for compress95 from 8 to 16 bytes, 0.39 from 32
to 64). The miss penalty is the other side of the trade-off. A longer block takes
longer to transfer, and a real cache would pay that on every miss. sim-outorder
charges a fixed 6 cycles for an L1 miss that hits in the L2, so our IPC curves
show almost no penalty. Even so, the lowest miss rate does not give the highest
IPC for compress95. 64 bytes has the lowest miss rate (4.31% against 4.70%), but
32 bytes has the slightly higher IPC, because the misses a longer block avoids
are cheap ones the core was already hiding. For cc1, 64 bytes is best on both
counts, by 0.06% in IPC. With a real, size-dependent miss penalty, 32 bytes would
be the better choice for both programs.

## Question (c): CPI per extra 100 cycles, with and without L2; value of an L2
Fitting a straight line through each curve, every extra 100 cycles of memory
latency costs 0.068 CPI for compress95 and 0.371 CPI for cc1 with the L2. Without
it the costs are 0.876 and 7.851 CPI, 13 and 21 times more. With an L2, only L1
misses that also miss in the L2 reach memory, and the L2 filters out most of
them (its miss rate was 9.9% and 4.2% in Part 1). Without it, every L1 miss pays
the full memory latency. The L2 makes the processor almost insensitive to how
slow main memory is, which matters more and more as memory falls further behind
the processor. For these programs, dropping the L2 to save area would be the
worst trade a designer could make.

## Question (d): which misses cause the damage without L2?
Graph 5 shows the L1 misses that go straight to memory when there is no L2.
compress95 has 0.16 instruction misses and 17.4 data misses per 1000
instructions, while cc1 has 80.8 instruction misses and 5.9 data misses. cc1 is
damaged by its instruction misses. Without an L2, each one stops fetch for the
whole memory latency, and the out-of-order core cannot hide that because no new
instructions arrive for it to execute. That is how cc1's CPI reaches 16.7 at 200
cycles. compress95 is damaged by data misses, which hurt less. While a load
waits, the RUU can still execute independent instructions that were already
fetched. Its CPI rises only to 2.3 at 200 cycles, 3.3 times its CPI with the L2,
compared with 9.3 times for cc1.

## Question (e): were the Part 1 predictions right?
Mostly, yes. In Part 1 we predicted that compress95 would react more to the L1
data cache. Growing it from 1 KB to 64 KB raises compress95's IPC by 10.9%
against 7.3% for cc1, and compress95 still misses 2.7% of the time at 64 KB when
cc1 has almost no misses left. We also predicted that cc1 would suffer more from
anything that makes instruction misses expensive, and that it would be the more
sensitive program overall. Removing the L2 multiplies cc1's CPI by 9.3 at 200
cycles against 3.3 for compress95, and its cost per 100 cycles of latency is 21
times higher. What we did not expect was how small the IPC gains from a bigger
L1 would be, since the L2 and out-of-order execution already hide most L1 data
misses.

## Observations / problems
- The 16 KB and 32-byte runs use the default configuration and give exactly the
  Part 3 RUU 16 results (compress95 1.7145, cc1 0.8849).
