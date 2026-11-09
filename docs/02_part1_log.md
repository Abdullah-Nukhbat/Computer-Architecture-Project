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
[Write 4-6 sentences. Base: loads, stores and branches together are about 54%
of compress95 and 59% of cc1. cc1 has more loads (25.4% vs 21.3%) and more
branches (20.1% vs 17.9%). Say what that implies: more memory and control
instructions means more chances to stall.]

### IPC
compress95 reaches IPC 1.71 and cc1 0.92, which is 43% and 23% of the peak of 4
for this 4-wide machine. [Explain why neither is near the peak: width is not
the limit, so cache misses and branch mispredictions must be.]

### Miss rates
cc1's L1 instruction cache misses 5.76% of references against 0.01% for
compress95, while compress95's L1 data cache misses 4.70% against 1.49% for cc1.
[Explain why: cc1 is a compiler with a large code footprint, compress95 uses a
big hash table that does not fit in the 16 KB data cache.]

### Branch mispredictions
The bimodal predictor is right 89.9% of the time on compress95 and 88.8% on cc1,
which is about 18.0 and 22.6 mispredictions per 1000 instructions.
[Explain: each misprediction throws away wrong-path work, so cc1 loses more.]

## Predictions (to be checked in Parts 4 and 5)

(i) Cache sensitivity: [your prediction. Base: compress95 should react to L1
data-cache changes (dl1 miss rate 4.7%), cc1 to instruction-cache changes
(il1 miss rate 5.8%), and cc1 has more loads overall (25%). Say which benchmark
you expect to be MORE sensitive overall and why.]

(ii) Branch-predictor sensitivity: [your prediction. Base: cc1 has more branches
(20.1% vs 17.9%) and higher MPKI (22.6 vs 18.0), so it should be more sensitive.]

## Observations / problems
- [Anything surprising or any error you hit while running the scripts.]