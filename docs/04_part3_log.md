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
0.86 to 1.87 (117%), but raises cc1's only from 0.62 to 0.92 (48%). Nearly all of
the gain comes early. Going from 4 to 16 entries buys compress95 0.071 IPC per
added entry and cc1 0.022, while going from 32 to 128 buys less than 0.0004 per
entry for both. A small window cannot look past a load that misses or a long
chain of dependent instructions, so the 4-wide core sits idle; a bigger window
lets it reach further ahead for independent work. compress95 is about twice as
sensitive as cc1 because, as Part 2 showed, it has more independent work to
find. The default 16 entries leaves 9% of compress95's performance unused, so a
32- to 64-entry window is the sensible size, and anything beyond that is
hardware that does nothing.

## Graph 2: average RUU occupancy (data/part3_g2_ruu_occupancy.png)
With a 4-entry RUU both programs keep it mostly full (3.4 and 2.4 entries on
average), but as the window grows, occupancy falls further and further behind
its size. compress95 reaches 12.4 entries at RUU 16, 24.2 at 64 and 27.6 at 128,
while cc1 levels off at about 10 (9.2 at 64, 10.1 at 128). Dividing occupancy by
IPC, an instruction spends about 7 cycles in the window at RUU 16 and 15 cycles
at RUU 128 for compress95, and 6 and 11 cycles for cc1, so most of the extra
occupancy is instructions waiting longer rather than more of them running in
parallel. Occupancy stops growing because instructions can only enter as fast as
the front end delivers correct-path work: every misprediction empties the
window, and each cc1 instruction miss stops fetch altogether. With a
misprediction every 56 instructions for compress95 and every 44 for cc1, a
128-entry window cannot be filled with useful work, and at that size compress95
uses less than a quarter of it and cc1 less than a tenth.

## Graph 3: fraction of cycles the RUU was full (data/part3_g3_ruu_full.png)
With 4 entries the RUU is full in 66% of cycles for compress95 and 37% for cc1,
so at that size the window is clearly the bottleneck and dispatch keeps
stopping for lack of room. compress95 still fills its window half the time at 16
entries (51%), then 18% at 32, 3.9% at 64 and 1.0% at 128. cc1 drops much faster:
12% at 16, 3.8% at 32 and under 1% from 64 entries on. A full window means
instructions are queuing to get in, so extra entries would be used at once; a
window that is almost never full has spare room that nothing arrives to fill.
The size at which the curve falls below about 5% matches where IPC stops
growing: around 32 entries for cc1 and 64 for compress95. This makes "how often
is the window full" a quick test of whether a bigger window is worth paying for.

## Graph 4: gain per doubling (data/part3_g4_gain_per_doubling.png)
Each doubling of the RUU is worth less than the one before: compress95 gains
60.5%, 23.9%, 7.2%, 1.4% and 0.5%, and cc1 27.8%, 11.1%, 3.7%, 0.5% and 0.1%. From
one doubling to the next the gain shrinks by a factor of 2.5 to 7, and faster
the larger the window already is. compress95 starts higher because it has more
ILP, but both programs follow the same shape. The last doubling worth more than
a couple of percent is 16 to 32 entries (7.2% and 3.7%). Since every doubling
also doubles the hardware and power of the RUU while the return keeps falling,
the cost-effective size is 32 entries for cc1 and 32 to 64 for compress95.

## Graph 5: W=8 with RUU 16 vs W=4 with RUU 64 (data/part3_g5_design_choice.png)
With W=8 and a 16-entry RUU, IPC is 1.883 for compress95 and 0.958 for cc1,
against 1.863 and 0.922 with W=4 and a 64-entry RUU, so the wider machine wins by
1.1% and 3.8%. The margin is small for compress95 because its 16-entry window is
full in 64% of cycles at W=8, compared with 4% for the W=4 machine with 64
entries, so it often cannot accept new instructions. cc1 barely notices the
smaller window: it uses only 5.8 of the 16 entries on average, so it keeps the
full benefit of fetching and committing 8 instructions per cycle after every
misprediction or instruction miss. Neither design comes close to its peak,
which shows that width and window size have to grow together.

## Question (a): where does a bigger window stop paying off?
For cc1 a bigger window stops paying off at about 32 entries. Going from 16 to 32
still gives 3.7%, but 32 to 64 gives only 0.5%. Graph 2 shows why: cc1's
occupancy levels off at 8 to 10 entries, and at 32 entries the RUU is full in
only 3.8% of cycles. For compress95 the useful limit is about 64 entries. Going
from 32 to 64 still gives 1.4% (64 to 128 only 0.5%), and its window is full 18%
of the time at 32 entries but only 3.9% at 64. In both programs the window stops
helping once occupancy no longer follows the RUU size and the window is rarely
full: the extra entries are there, but nothing arrives to fill them.

## Question (b): why does a larger window hide cache-miss latency, and why is the benefit limited by mispredictions?
When a load misses in the L1 data cache it waits 6 cycles for the L2, or 18 or
more for memory, and it cannot commit, so the oldest entry in the RUU is stuck.
Instructions behind it keep arriving, and the ones that do not need the load's
result can execute out of order. The more entries the RUU has, the more of this
independent work fits behind the waiting load, so the miss overlaps with useful
work instead of stopping the machine. compress95 shows this best: it misses in
the data cache 17 times per 1000 instructions and gains 117% from a larger
window. The window only holds useful work up to the next mispredicted branch,
though. Everything fetched after it is on the wrong path and is thrown away when
the branch resolves. With 18.0 (compress95) and 22.6 (cc1) mispredictions per
1000 instructions, there is one every 56 and 44 instructions on average, which
is why occupancy levels off at 28 and 10 entries and a 128-entry window can never
be filled with correct-path work.

## Question (c): W=8 with RUU 16, or W=4 with RUU 64?
We would choose W=8 with a 16-entry RUU. It is faster on both benchmarks, by 1.1%
on compress95 (1.883 against 1.863) and 3.8% on cc1 (0.958 against 0.922). For
cc1 the choice is easy given Parts 2 and 3: it never uses more than about 10
window entries, so a 16-entry RUU costs it almost nothing, while the wider fetch
refills the pipeline faster after each misprediction and instruction miss. For
compress95 the two designs are close, because at W=8 its 16-entry window is full
64% of the time and wastes much of the extra width. This conclusion holds for
our two benchmarks only, and under the Part 6 cost model the wider design is also
the more expensive one (36 units against 32).

## Observations / problems
- The RUU 16 runs use the default configuration and give exactly the Part 1 IPC
  for compress95 (1.7145). cc1 differs (0.8849 against 0.9204) because Part 1
  runs it to completion while Part 3 stops at 100 million instructions.
