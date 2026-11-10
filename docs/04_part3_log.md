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
[paste the table printed by part3_graphs.py]

## Graph 1: IPC vs RUU size
[4-6 sentences. Numbers first: IPC at RUU 4 and at RUU 128 for each benchmark
and the percentage change. Then why. Compare the two benchmarks and say which
is more sensitive. End with a design conclusion.]

## Graph 2: average RUU occupancy
[3-5 sentences. Compare occupancy to the RUU size. Where does occupancy stop
growing even though the window gets bigger? What does that say?]

## Graph 3: fraction of cycles the RUU was full
[3-5 sentences. At which sizes is the window full often? When the full fraction
falls to near zero, the window is no longer the bottleneck.]

## Graph 4: gain per doubling
[2-4 sentences. Where does the gain fall below a few percent?]

## Question (a): where does a bigger window stop paying off?
[For each benchmark, give the size and the evidence from Graphs 1 to 4,
relating it to the occupancy graph.]

## Question (b): why does a larger window hide cache-miss latency, and why is the benefit limited by mispredictions?
[Hints to put in your own words: when a load misses, the oldest instruction
cannot commit, but a larger window lets the processor keep fetching and
executing younger independent instructions during the miss. A larger window
only helps if those instructions are on the correct path. After a
misprediction the window fills with wrong-path work that is thrown away, so
the useful window is limited by how far the predictor can run before it makes
a mistake. Use your MPKI numbers (18.0 and 22.6) and dl1/il1 miss rates.]

## Question (c): W=8 with RUU 16, or W=4 with RUU 64?
[Quote the four IPC values from Graph 5, say which you would choose and why,
using Parts 2 and 3: Part 2 showed extra width alone is poorly used, Part 3
shows the window sets how much parallelism can be exposed. Mention that the
choice is for these two benchmarks only.]

## Observations / problems
- [anything surprising]