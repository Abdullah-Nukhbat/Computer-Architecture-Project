# Part 3 log: Instruction window (RUU) size

## Setup
- Scripts: scripts/run_P3.sh (14 runs), scripts/part3_graphs.py
- Width fixed at the default 4; -max:inst 100000000
- RUU = 4, 8, 16, 32, 64, 128 with -lsq:size = RUU/2
- Extra runs for question (c): W=8 (ifqsize/decode/issue/commit/ialu = 8, memport 4), RUU 16, LSQ 8
- Raw outputs: results/*_P3_ruu*.txt and results/*_P3c_W8_ruu16.txt
- Data: data/part3_table.csv, data/part3c_table.csv
- Check: the RUU 64 runs match the Part 2 W=4 out-of-order runs.

## Results table
| Benchmark | RUU | LSQ | IPC | Avg. RUU occupancy | Occupancy % of RUU | RUU full |
|---|---|---|---|---|---|---|
| compress95 | 4 | 2 | 0.8617 | 3.4 | 84.3% | 66.3% |
| compress95 | 8 | 4 | 1.3833 | 6.7 | 83.8% | 64.7% |
| compress95 | 16 | 8 | 1.7145 | 12.4 | 77.5% | 51.2% |
| compress95 | 32 | 16 | 1.8372 | 18.8 | 58.8% | 18.3% |
| compress95 | 64 | 32 | 1.8629 | 24.2 | 37.8% | 3.9% |
| compress95 | 128 | 64 | 1.8727 | 27.6 | 21.6% | 1.0% |
| cc1 | 4 | 2 | 0.6233 | 2.4 | 59.8% | 37.2% |
| cc1 | 8 | 4 | 0.7968 | 3.7 | 46.6% | 24.3% |
| cc1 | 16 | 8 | 0.8849 | 5.5 | 34.2% | 11.5% |
| cc1 | 32 | 16 | 0.9180 | 7.8 | 24.2% | 3.8% |
| cc1 | 64 | 32 | 0.9222 | 9.2 | 14.4% | 0.9% |
| cc1 | 128 | 64 | 0.9230 | 10.1 | 7.9% | 0.3% |

Question (c):

| Benchmark | W=8, RUU 16 | W=4, RUU 64 |
|---|---|---|
| compress95 | 1.8827 | 1.8629 |
| cc1 | 0.9575 | 0.9222 |

## Graph 1: IPC vs RUU size (data/part3_g1_ipc_vs_ruu.png)
Growing the RUU from 4 to 128 entries more than doubles compress95's IPC, from
0.86 to 1.87 (+117%), but raises cc1's only from 0.62 to 0.92 (+48%). Almost all
of the gain comes from the small sizes: going from 4 to 16 entries gives
compress95 +99% and cc1 +42%, while 32 to 128 adds only +1.9% and +0.5%. A tiny
window cannot look far enough ahead to find independent instructions, so the
4-wide machine sits idle behind every load that misses or every long dependence
chain. Once the window holds more independent work than the program offers
between two mispredictions, extra entries stay empty. compress95 is about twice
as sensitive as cc1 because it has more ILP (Part 2): it has more independent
work for a larger window to find. For a designer, the default of 16 entries
leaves 9% of compress95's performance unused, but beyond 32 to 64 entries the
extra hardware is wasted.

## Graph 2: average RUU occupancy (data/part3_g2_ruu_occupancy.png)
With 4 entries both programs keep the window mostly full (3.4 and 2.4 entries,
84% and 60% of it). As the RUU grows, compress95's average occupancy keeps rising
but ever more slowly, from 12.4 at 16 entries to 24.2 at 64 and 27.6 at 128,
while cc1 levels off at about 10 entries (9.2 at 64, 10.1 at 128). The occupancy
stops growing because instructions cannot enter the window faster than the
front end delivers correct-path instructions: every misprediction empties the
window, and cc1's instruction-cache misses stop fetch altogether. A window can
only be filled as far as the program runs between two such events, which is
about 56 instructions for compress95 and 44 for cc1, and on average much less.
So a 128-entry RUU is less than a quarter used by compress95 and less than a
tenth by cc1.

## Graph 3: fraction of cycles the RUU was full (data/part3_g3_ruu_full.png)
With 4 entries the RUU is full in 66.3% of cycles for compress95 and 37.2% for
cc1, so the window is clearly the bottleneck at that size. compress95 still has
a full window half the time at 16 entries (51.2%), but only 18.3% at 32, 3.9% at
64 and 1.0% at 128. cc1 drops faster: 11.5% at 16, 3.8% at 32 and below 1% from
64 on. When the window is almost never full, adding entries cannot help, because
dispatch is not being blocked by a lack of space; this happens at about 32
entries for cc1 and 64 for compress95.

## Graph 4: gain per doubling (data/part3_g4_gain_per_doubling.png)
Each doubling of the RUU is worth less than the one before: compress95 gains
+60.5%, +23.9%, +7.2%, +1.4% and +0.5%, and cc1 +27.8%, +11.1%, +3.7%, +0.5% and
+0.1%. The gain falls below a few percent after 32 entries for compress95 and
after 16 to 32 entries for cc1.

## Question (a): where does a bigger window stop paying off?
For cc1, the window stops paying off at about 32 entries. Going from 16 to 32
still gives +3.7%, but 32 to 64 gives only +0.5%. At the same point average
occupancy levels off at about 8 to 10 entries, and the RUU is full in only 3.8%
of cycles at 32 entries. For compress95 the useful limit is about 64 entries:
32 to 64 still gives +1.4% (64 to 128 gives +0.5%), and the RUU is full 18.3% of
the time at 32 entries but only 3.9% at 64. In both cases the window stops
helping once occupancy stops tracking the RUU size and the window is rarely
full: the extra entries exist but nothing arrives to fill them.

## Question (b): why does a larger window hide cache-miss latency, and why is the benefit limited by mispredictions?
When a load misses in the L1 data cache it waits 6 cycles for the L2, or 18 or
more for memory, and it cannot commit, so the oldest RUU entry is blocked.
Instructions behind it keep arriving, and those that do not depend on the load
can execute out of order. The more entries the RUU has, the more independent
instructions fit behind the stalled load, so the miss is overlapped with useful
work instead of stopping the machine. compress95 shows this most clearly: it
misses in the data cache 17 times per 1000 instructions and gains +117% from a
larger window. But the window only holds useful work up to the next
mispredicted branch: everything fetched after it is on the wrong path and is
thrown away when the branch resolves. With 18.0 (compress95) and 22.6 (cc1)
mispredictions per 1000 instructions, there is on average one every 56 and 44
instructions, which is why occupancy saturates at 28 and 10 entries and a
128-entry window cannot be filled with correct-path work.

## Question (c): W=8 with RUU 16, or W=4 with RUU 64?
The extra runs give IPC 1.883 (compress95) and 0.958 (cc1) for W=8 with a 16-entry
RUU, against 1.863 and 0.922 for W=4 with a 64-entry RUU. The W=8/RUU 16 design is
faster on both benchmarks, by 1.1% for compress95 and 3.8% for cc1, so we would
choose it. For cc1 this is clear from Parts 2 and 3: it never uses more than
about 10 RUU entries, so a 16-entry window loses almost nothing, while the wider
fetch refills the pipeline faster after each misprediction and instruction-cache
miss. For compress95 the two are close: W=8 gains width but its RUU 16 is often
full (51% of cycles at W=4), so it gives back most of the advantage. This choice
holds for these two benchmarks only, and under the Part 6 cost model the wider
design is also more expensive (32 + 4 = 36 units against 16 + 16 = 32).

## Observations / problems
- The RUU 16 runs are the default configuration and give exactly the Part 1
  IPC for compress95 (1.7145). cc1 differs (0.8849 against 0.9204) only because
  Part 1 ran cc1 to completion and Part 3 stops at 100 million instructions.
