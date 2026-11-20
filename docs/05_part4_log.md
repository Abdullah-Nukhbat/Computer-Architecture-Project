# Part 4 log: Memory hierarchy

## Setup
- Scripts: scripts/run_P4.sh (32 required runs + 4 extra), scripts/part4_graphs.py
- Fixed: -max:inst 100000000, default width 4, RUU 16, LSQ 8
- (a) capacity: dl1:8/32/128/512:32:4:l (1, 4, 16, 64 KB)
- (b) block size: dl1:512:8, 256:16, 128:32, 64:64 (16 KB, 4-way)
- (c) -mem:lat 25/50/100/200 2, with default L2 and with -cache:dl2 none -cache:il2 none
- Extra (3C): 16 KB direct-mapped (dl1:512:32:1:l) and 16-way (dl1:32:32:16:l)
- Raw outputs: results/*_P4*.txt   Data: data/part4_table.csv

## Results tables
[paste the tables printed by part4_graphs.py]

## Graphs 1a, 1b: capacity
[4-6 sentences. Numbers first: dl1 miss rate and IPC at 1 KB and at 64 KB for
each benchmark, with percentage changes. Then why. Compare the benchmarks. End
with a design conclusion.]

## Graphs 2a, 2b: block size
[4-6 sentences. Numbers first, then why.]

## Graph 3: CPI vs memory latency
[4-6 sentences. Numbers first, then why.]

## Question (a): compulsory, capacity, conflict misses
[Compulsory = first touch of a block, cannot be removed by any cache size, so
the miss rate at 64 KB is roughly the floor. Capacity = the drop as the cache
grows from 1 KB to 16/64 KB. Conflict = the difference between direct-mapped
and 4-way/16-way at the same 16 KB (Graph 6). Use your numbers to explain the
SHAPE of the capacity graph for each benchmark.]

## Question (b): block size
[Spatial locality: bigger blocks bring in neighbouring data, cutting misses.
But a bigger block takes longer to fetch from memory (higher miss penalty) and
fewer blocks fit (more conflict/pollution). Is the block size with the lowest
miss rate also the one with the highest IPC? Answer with your numbers.]

## Question (c): value of the L2
[From the linear fit: extra CPI per 100 cycles of memory latency, with L2 and
without. Compare and say what it means for the value of an L2.]

## Question (d): which misses cause the damage without an L2?
[Use il1 and dl1 misses per 1000 instructions (Graph 5) and the slowdown
(Graph 4) for each benchmark. State which kind of L1 miss hurts each
benchmark.]

## Question (e): were the Part 1 predictions correct?
[Part 1 predicted: [copy your two predictions here]. Say whether each was right
and why, using Parts 4 numbers.]

## Observations / problems
- [anything surprising]