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


## 1(c) Charts

- data/part1_instruction_mix.png  (stacked bar: loads / stores / branches / other)
- data/part1_ipc.png
- data/part1_miss_rates.png
- data/part1_mpki.png

### Instruction mix (data/part1_instruction_mix.png)
Loads, stores and branches make up 53.6% of compress95's instructions and 59.2%
of cc1's. cc1 has more loads (25.4% against 21.3%) and more branches (20.1%
against 17.9%), while the two store at about the same rate (13.7% and 14.5%). Put
another way, cc1 meets a branch every 5.0 instructions and compress95 every 5.6,
and 39% of cc1's instructions touch memory against 36% of compress95's. That fits
what the two programs do: a compiler spends its time following pointers through
syntax trees and symbol tables and deciding what to do next, while compress95
runs one tight loop over a buffer. On instruction mix alone, cc1 gives both the
memory system and the branch predictor more work, so we expect it to be the
slower and more sensitive of the two.

### IPC (data/part1_ipc.png)
compress95 runs at IPC 1.71 and cc1 at 0.92, only 43% and 23% of the 4-wide
machine's peak, so neither program is held back by width. The gap between them
is 0.50 cycles per instruction (CPI 1.09 against 0.58), and most of it comes from
the instruction cache. cc1 misses there 76.3 times per 1000 instructions, and if
each miss stalls fetch for the 6-cycle L2 hit time, that alone adds
76.3 x 6 / 1000 = 0.46 CPI. compress95 has almost no instruction misses (0.16 per
1000), and even if none of its 17.4 data misses per 1000 instructions were
hidden, they would add only 0.10 CPI. Instruction misses are so costly because the
out-of-order core cannot work around them: while fetch waits, there are no new
instructions to execute. A program like cc1 needs a better instruction supply
before a wider core can do anything for it.

### Miss rates (data/part1_miss_rates.png)
cc1's L1 instruction cache misses 5.76% of its accesses against only 0.01% for
compress95, while the data cache shows the opposite: 4.70% for compress95
against 1.49% for cc1. A whole C compiler's code is much larger than the 16 KB
direct-mapped instruction cache, while compress95's hot loop fits easily and
misses only 13,089 times in 80 million instructions. compress95's data, on the
other hand, is a large hash table read at scattered positions, which a 16 KB
data cache cannot hold. Most of these misses are caught by the L2, which misses
only 9.9% of its accesses for compress95 and 4.2% for cc1, so main memory is
rarely reached. The two benchmarks stress opposite halves of the memory system,
compress95 the data side and cc1 the instruction side, which makes them a useful
pair for the cache experiments in Part 4.

### Branch mispredictions (data/part1_mpki.png)
The default bimodal predictor is right 89.9% of the time on compress95 and 88.8%
on cc1, which works out to 18.0 and 22.6 mispredictions per 1000 instructions.
The accuracies look close, but cc1 also has more branches (20.1% of instructions
against 17.9%), so it ends up with 26% more mispredictions per instruction. That
leaves compress95 about 56 instructions between two mispredictions and cc1 only
44. Every misprediction throws away the wrong-path instructions fetched after
the branch, so the window can never hold more useful work than the stretch
between two mispredictions. A compiler's branches depend on the program it is
compiling, which makes them harder to learn than the loop branches that repeat
in compress95. On these numbers cc1 should gain more from a better predictor,
which Part 5 tests.

## Predictions (to be checked in Parts 4 and 5)

(i) Cache sensitivity: we expect compress95 to react more to changes in the L1
data cache. Its data miss rate (4.7%) is three times cc1's and its hash table is
larger than 16 KB, so every increase in data-cache size should keep removing
misses. cc1 should react more to anything that makes instruction misses more
expensive, such as removing the L2 or slowing main memory, because its 76
instruction misses per 1000 instructions stop fetch completely and out-of-order
execution cannot hide them. Overall, we expect cc1 to suffer more from a weaker
memory system.

(ii) Branch-predictor sensitivity: cc1 has more branches (20.1% against 17.9%)
and more mispredictions (22.6 against 18.0 per 1000 instructions), so we expect
cc1 to be more sensitive to the branch predictor than compress95.

## Observations / problems
- cc1's IPC over the full run (0.920) is higher than over its first 100 million
  instructions with the same configuration (0.885 in Part 3), so the later part
  of the compilation runs faster than the start.
