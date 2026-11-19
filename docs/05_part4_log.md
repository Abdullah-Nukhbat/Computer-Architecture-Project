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
Growing the L1 data cache from 1 KB to 64 KB cuts compress95's miss rate from
9.45% to 2.68% and cc1's from 11.41% to 0.35%. cc1 starts higher but falls much
faster: by 16 KB it misses only 1.42% of accesses, and at 64 KB almost
everything fits. compress95 improves steadily but slowly, losing 26% to 43% of
its misses with each 4x step, and still misses 2.68% at 64 KB. This shows the two
programs have very different working sets: most of cc1's data accesses go to a
set of data that fits in about 16 KB, while compress95's hash table is larger
than 64 KB and is accessed at scattered positions. A bigger data cache is
therefore worth much more to compress95 at the sizes a designer would actually
build (16 KB and up).

## Graph 1b: IPC vs capacity (data/part4_g2_ipc_vs_capacity.png)
IPC rises from 1.601 to 1.775 (+10.9%) for compress95 and from 0.837 to 0.898
(+7.3%) for cc1 between 1 KB and 64 KB. These gains are small compared with the
change in miss rate: cc1's miss rate falls by a factor of 33 but its IPC rises
only 7%. Two things hide the extra misses. Almost all of them hit in the L2,
which costs only 6 cycles, and the out-of-order core keeps executing independent
instructions during those 6 cycles. Only about a quarter of instructions are
loads (21% and 25%), so even a large miss-rate change touches few instructions.
compress95 gains more because it has more data misses left to remove (2.7%
still at 64 KB against 0.35%) and more ILP to use once they are gone.

## Graph 2a: dl1 miss rate vs block size (data/part4_g3_dl1_miss_vs_block.png)
With the capacity fixed at 16 KB, longer blocks reduce the miss rate for both
programs: from 7.79% to 4.31% for compress95 and from 2.41% to 1.28% for cc1
between 8 and 64 bytes. Each doubling helps less than the one before (32 to 64
bytes removes only 0.39 points for compress95 and 0.14 for cc1). A longer block
brings in the neighbouring words of the one that missed, and programs often use
those soon (spatial locality), so many future misses become hits. But with a
fixed capacity, longer blocks mean fewer blocks: a 64-byte-block 16 KB cache
holds only 256 blocks, so data that is not near other used data is evicted
sooner, which is why the gain shrinks.

## Graph 2b: IPC vs block size (data/part4_g4_ipc_vs_block.png)
IPC hardly changes with block size: compress95 goes from 1.7014 at 8 bytes to
1.7145 at 32 bytes (+0.8%) and cc1 from 0.8818 to 0.8854 at 64 bytes (+0.4%),
even though the miss rate drops by 45% and 47%. For compress95 the 64-byte block
has the lowest miss rate (4.31%) but not the highest IPC: 1.7144 against 1.7145
at 32 bytes, which is a tie. The misses that longer blocks remove are the easy
ones: neighbouring words of a block that was just loaded, which the out-of-order
core would mostly have overlapped anyway. The scattered hash-table misses that
really stall compress95 are not helped by spatial locality. Note that in
sim-outorder an L1 miss that hits in the L2 costs a fixed 6 cycles whatever the
L1 block size, so these runs do not charge longer blocks a longer transfer; in
real hardware a 64-byte refill takes longer than a 32-byte one, which would
make the longest block lose.

## Graph 3: CPI vs memory latency (data/part4_g5_cpi_vs_latency.png)
With the L2 in place, raising main-memory latency from 25 to 200 cycles moves
CPI only from 0.588 to 0.707 for compress95 and from 1.155 to 1.805 for cc1.
Without the L2, CPI explodes: from 0.784 to 2.317 for compress95 and from 2.978
to 16.717 for cc1, where the machine needs almost 17 cycles per instruction.
(The y-axis is log scale so that all four lines are visible.) The lines are
almost straight, which means every extra cycle of memory latency is paid by a
fixed fraction of instructions: the ones whose miss goes all the way to memory.
cc1 without an L2 is by far the worst case because every instruction-cache miss
goes to memory.

## Graph 4 (extra): 3C breakdown (data/part4_g6_3c_breakdown.png)
See question (a).

## Graph 5 (extra): L1 misses per 1000 instructions (data/part4_g7_l1_misses_per_1000.png)
See question (d).

## Question (a): classify the misses (3 Cs), explain the capacity graph
The extra runs split every miss into the 3 Cs. Compulsory misses are tiny and
constant: 0.068% of data accesses for compress95 and 0.055% for cc1 at every
size, because each block is loaded once for the first time and then reused many
times during 100 million instructions. Conflict misses are small with a 4-way
cache and shrink as the cache grows (0.54% to 0.11% for compress95, 0.83% to
0.07% for cc1). Almost all of the misses are capacity misses: at 16 KB they are
4.33 of compress95's 4.70 points and 1.22 of cc1's 1.42. The capacity graph is
therefore the curve of capacity misses: each time the cache grows, more of the
working set fits. cc1's capacity misses fall from 10.5% to 0.23% because its
data fits by 16 to 64 KB, while compress95 still has 2.5% capacity misses at 64 KB
because its hash table is larger than that.

## Question (b): block size, spatial locality, miss penalty; lowest miss rate = highest IPC?
Spatial locality explains why the miss rate falls with longer blocks: a miss on
one word also brings in the words around it, and the next accesses often fall
there. With a fixed 16 KB, though, longer blocks mean fewer of them, so the gain
per doubling shrinks (from -2.10 to -0.39 points for compress95). The miss
penalty is the other side of the trade-off: a longer block takes longer to
transfer, and a real cache would pay that on every miss. In sim-outorder an L1
miss that hits in the L2 costs a fixed 6 cycles regardless of block size, so our
IPC curves show almost no penalty. Even so, the lowest miss rate does not give
the highest IPC for compress95: 64 bytes has the lowest miss rate (4.31% against
4.70%) but 32 bytes has the (very slightly) highest IPC, because the extra misses
avoided are cheap ones the core already hid. For cc1, 64 bytes is best on both,
by 0.06% in IPC. With a real, size-dependent miss penalty, 32 bytes would be the
better choice for both.

## Question (c): CPI per extra 100 cycles, with and without L2; value of an L2
Fitting a straight line through each curve, every extra 100 cycles of memory
latency costs 0.068 CPI for compress95 and 0.371 CPI for cc1 with the L2,
against 0.876 and 7.851 CPI without it, which is 13 and 21 times more. With an
L2, only L1 misses that also miss in the L2 reach memory, and the L2 filters out
most of them (its miss rate was 9.9% and 4.2% in Part 1). Without it, every L1
miss pays the full memory latency. The L2 makes the processor almost
insensitive to how slow main memory is, which matters because memory latency
in cycles keeps growing as processors get faster. Removing it to save area would
be the worst possible trade for these programs.

## Question (d): which misses cause the damage without L2?
Graph 5 shows the L1 misses that go straight to memory when there is no L2:
compress95 has 0.16 instruction misses and 17.4 data misses per 1000
instructions, while cc1 has 80.8 instruction misses and 5.9 data misses. cc1 is
damaged by instruction misses: without an L2, each of them stops fetch for the
whole memory latency, and the out-of-order core cannot hide that because no new
instructions arrive to execute. This is why cc1's CPI reaches 16.7 at 200
cycles. compress95 is damaged by data misses, which hurt less: while a load
waits, the RUU can still execute independent instructions that were already
fetched, so its CPI rises to only 2.3 at 200 cycles (x3.3 against x9.3 for cc1).

## Question (e): were the Part 1 predictions right?
Mostly yes. Part 1 predicted that compress95 would be more sensitive to the L1
data cache: growing it from 1 KB to 64 KB raises compress95's IPC by 10.9%
against 7.3% for cc1, and compress95 still has 2.7% data misses where cc1 has
almost none. Part 1 also predicted that cc1 would suffer more from anything that
makes instruction misses expensive, and that it would be the more sensitive
benchmark overall: removing the L2 multiplies cc1's CPI by 9.3 at 200 cycles
against 3.3 for compress95, and its latency cost is 21 times higher. One thing
we did not expect is how small the IPC gains from a bigger L1 are, because the
L2 and out-of-order execution already hide most L1 data misses.

## Observations / problems
- The fully-associative runs use 32 to 2048 ways in one set; the simulator
  models them with a hash table, so they run as fast as the normal caches.
