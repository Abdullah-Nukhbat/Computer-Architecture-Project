# Part 1 log: Baseline and verification

## 1(a) Correctness proof

Commands (from scripts/run_P1.sh, run from BenchMarks_Little/Input, full run, no -max:inst):

    diff results/compress95_P1.out ../Expected_Output/compress95.out
    diff results/cc1_P1_1stmt.s ../Expected_Output/1stmt.s

Output (results/P1_diff.txt):

    == diff compress95 ==
    == diff cc1 ==

Both diffs are empty, so both programs produce exactly the expected output on the simulator.

## 1(b) Baseline table (default configuration, full run)

| | compress95 | cc1 |
|---|---|---|
| sim_num_insn | 80,432,477 | 279,206,786 |
| sim_cycle | 46,912,553 | 303,355,315 |
| sim_IPC | 1.7145 | 0.9204 |
| sim_CPI | 0.5833 | 1.0865 |
| Loads (%) | 21.3 | 25.4 |
| Stores (%) | 14.5 | 13.6 |
| Branches (%) | 17.9 | 20.1 |
| il1.miss_rate | 0.0001 | 0.0576 |
| dl1.miss_rate | 0.0470 | 0.0149 |
| ul2.miss_rate | 0.0990 | 0.0415 |
| bpred_bimod.bpred_dir_rate | 0.8992 | 0.8877 |
| MPKI (bimodal) | 18.0 | 22.6 |

Full data: data/part1_table.csv. Raw outputs: results/compress95_P1.txt, results/cc1_P1.txt.

Note: the instructor's primer quotes IPC 0.88 for cc1 because it used only the
first 100M instructions. My run is the full 279M, so 0.92 is expected.

## 1(c) Charts

- data/part1_instruction_mix.png  (stacked bar: loads / stores / branches / other)
- data/part1_ipc.png
- data/part1_miss_rates.png
- data/part1_mpki.png

### Instruction mix
Loads, stores and branches together make up 53.6% of compress95's instructions
and 59.2% of cc1's, so cc1 has fewer plain ALU instructions (40.8% "other"
against 46.4%). cc1 has more loads (25.4% against 21.3%) and more branches
(20.1% against 17.9%), while the two programs store at a similar rate (13.7% and
14.5%). A branch every 5 instructions is typical of integer code: cc1 is a
compiler that spends its time walking trees and lists and deciding what to do
next, while compress95 runs one tight compression loop over a buffer. More
loads give more chances to wait on the data cache, and more branches give more
chances to mispredict and throw work away, so on instruction mix alone cc1
should be the slower and more sensitive program.

### IPC
compress95 reaches IPC 1.71 and cc1 only 0.92, which is 43% and 23% of the peak
of 4 on this 4-wide machine. Neither comes close to the peak, so the width is
not what limits them. For compress95 the main losses are 18.0 branch
mispredictions and 17.4 data-cache misses per 1000 instructions. cc1 suffers
from the same problems, plus 76.3 instruction-cache misses per 1000 instructions:
when the front end cannot fetch, there is nothing in the window to execute. The
result is that cc1 needs 1.09 cycles per instruction against 0.58 for
compress95, even though both run on the same hardware.

### Miss rates
cc1's L1 instruction cache misses 5.76% of accesses against 0.01% for
compress95, while compress95's L1 data cache misses 4.70% against 1.49% for cc1.
cc1 is a large program (a whole C compiler) whose code does not fit in the 16 KB
direct-mapped instruction cache, whereas compress95's hot code is small enough
to stay in the cache (only 13,089 instruction misses in 80 million instructions). compress95's data, however, is a large hash table
accessed at effectively random positions, which a 16 KB data cache cannot hold.
The L2 catches most of these misses (it misses 9.9% of its accesses for
compress95 and 4.2% for cc1), so main memory is reached only rarely. The two
benchmarks therefore stress opposite sides of the memory system: compress95 the
data side, cc1 the instruction side.

### Branch mispredictions
The bimodal predictor is right 89.9% of the time on compress95 and 88.8% on cc1,
which is 18.0 and 22.6 mispredictions per 1000 instructions. Accuracy alone hides
the difference: cc1 has more branches (20.1% of instructions against 17.9%), so
its slightly lower accuracy turns into 26% more mispredictions per instruction.
Each misprediction squashes every wrong-path instruction fetched after the
branch and restarts fetch, so on a 4-wide machine one misprediction can waste
several cycles of up to 4 instructions each. A compiler's branches depend on the
input program being compiled, which makes them hard to predict, while
compress95's loop branches repeat in regular patterns.

## Predictions (to be checked in Parts 4 and 5)

(i) Cache sensitivity: compress95 should be the more sensitive benchmark to
changes in the L1 data cache, because its dl1 miss rate (4.7%) is three times
cc1's and its hash table is larger than 16 KB, so a bigger data cache keeps
removing misses. cc1 should be the more sensitive benchmark to anything that
makes instruction misses more expensive, such as removing the L2 or slowing
main memory, because its 76 instruction-cache misses per 1000 instructions stall
fetch completely and cannot be hidden by out-of-order execution. Overall we
expect cc1 to suffer more from a weaker memory system.

(ii) Branch-predictor sensitivity: cc1 has more branches (20.1% against 17.9%)
and a higher misprediction rate (22.6 MPKI against 18.0), so we predict that cc1
will be more sensitive to the branch predictor than compress95.

## Observations / problems
- cc1's IPC for the full run (0.920) is higher than for its first 100 million
  instructions with the same configuration (0.885, Part 3 RUU 16), so the later
  part of the compilation runs faster than the start.
- compress95 commits 80,432,477 instructions here but 80,432,502 in Parts 2-6.
  Part 1 writes the program's output to a file and later parts send it to
  /dev/null, which most likely changes how the program buffers its output. IPC
  is identical (1.7145) wherever the configuration is the same.
