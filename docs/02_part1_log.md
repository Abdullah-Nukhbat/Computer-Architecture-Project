# Part 1 log: Baseline and verification

## 1(a) Correctness proof

Commands (from scripts/run_P1.sh, run from BenchMarks_Little/Input, full run, no -max:inst):

    diff results/compress95_P1.out ../Expected_Output/compress95.out
    diff results/cc1_P1_1stmt.s ../Expected_Output/1stmt.s

Output (results/P1_diff.txt):

    == diff compress95 ==
    == diff cc1 ==

Both diffs are empty. The simulated programs produce exactly the expected output, which tells us the simulator and benchmarks are set up correctly before we start changing anything.

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
against 17.9%), while both programs store at about the same rate (13.7% and
14.5%). That means cc1 meets a branch every 5.0 instructions and compress95
every 5.6, and 39% of cc1's instructions touch memory compared with 36% for
compress95. This matches what the programs actually do. A compiler spends most
of its time following pointers through syntax trees and symbol tables and
deciding what to do next, while compress95 keeps running one tight loop over a
buffer. Going by instruction mix alone, cc1 gives both the memory system and the
branch predictor more work, and we would expect it to be the slower and more
sensitive of the two.

### IPC (data/part1_ipc.png)
compress95 runs at IPC 1.71 and cc1 at 0.92. That is only 43% and 23% of the
4-wide machine's peak, so width is not what holds either of them back. The gap
between them is 0.50 cycles per instruction (CPI 1.09 against 0.58), and most of
it comes from the instruction cache. cc1 misses there 76.3 times per 1000
instructions. If each of those misses stalls fetch for the 6-cycle L2 hit time,
they add 76.3 x 6 / 1000 = 0.46 CPI, almost the whole gap. compress95 has hardly
any instruction misses (0.16 per 1000), and even if none of its 17.4 data misses
per 1000 instructions were hidden they would only add 0.10 CPI. Instruction
misses hurt so much because the out-of-order core has nothing to work on while
fetch is waiting. For a program like cc1, a better instruction supply has to come
before a wider core can make any difference.

### Miss rates (data/part1_miss_rates.png)
cc1's L1 instruction cache misses 5.76% of its accesses, compared with only 0.01%
for compress95. The data cache is the other way round, with 4.70% for compress95
and 1.49% for cc1. A whole C compiler's code is much bigger than the 16 KB
direct-mapped instruction cache, while compress95's hot loop fits easily and
misses only 13,089 times in 80 million instructions. compress95's data is a
large hash table that it reads at scattered positions, and a 16 KB data cache
cannot hold it. The L2 catches most of these misses (it misses only 9.9% of its
accesses for compress95 and 4.2% for cc1), so main memory is rarely reached. In
short, compress95 stresses the data side of the memory system and cc1 the
instruction side, which makes them a useful pair for the cache experiments in
Part 4.

### Branch mispredictions (data/part1_mpki.png)
The default bimodal predictor is right 89.9% of the time on compress95 and 88.8%
on cc1. That works out to 18.0 and 22.6 mispredictions per 1000 instructions.
The two accuracies look close, but cc1 also has more branches (20.1% of its
instructions against 17.9%), and together that gives it 26% more mispredictions
per instruction. compress95 gets through about 56 instructions between two
mispredictions and cc1 only 44. Each misprediction throws away everything
fetched after the branch, and the window can never hold more useful work than
the stretch between two mispredictions. A compiler's branches depend on the
program it is compiling, which makes them harder to learn than the loop branches
that keep repeating in compress95. Based on these numbers we expected cc1 to
gain more from a better predictor, and Part 5 tests that.

## Predictions (to be checked in Parts 4 and 5)

(i) Cache sensitivity. We expect compress95 to react more to changes in the L1
data cache. Its data miss rate (4.7%) is three times cc1's and its hash table is
bigger than 16 KB, so every increase in data-cache size should keep removing
misses. cc1 should react more to anything that makes instruction misses more
expensive, like removing the L2 or slowing down main memory. Its 76 instruction
misses per 1000 instructions stop fetch completely, and out-of-order execution
cannot hide that. Overall we expect cc1 to suffer more from a weaker memory
system.

(ii) Branch-predictor sensitivity. cc1 has more branches (20.1% against 17.9%)
and more mispredictions (22.6 against 18.0 per 1000 instructions). We therefore
expect cc1 to be more sensitive to the branch predictor than compress95.

## Observations / problems
- cc1's IPC over the full run (0.920) is higher than over its first 100 million
  instructions with the same configuration (0.885 in Part 3). The later part of
  the compilation runs faster than the start.
