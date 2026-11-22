# Part 6 log: Design your own processor

## 1. Setup

- **Goal:** highest geometric-mean IPC of compress95 and cc1 within 100 cost units
- **Scripts:**
  - `scripts/part6_designs.py`: cost model and candidate list
  - `scripts/run_P6.py`: runs the designs
  - `scripts/part6_graphs.py`: table, graphs, final config
  - `scripts/P6_commands.sh`: every exact command
- **Every run uses:** `-max:inst 100000000`
- **Left at defaults:** memory latency, cache latencies, `-res:imult`, FP units, BTB, RAS
- **Cost check:** the script prints the default design's cost as 86.00, matching the statement
- **Size of the search:** 42 designs (D01 to D43, D30 dropped), 84 runs
- **Raw outputs:** `results/*_P6_*.txt`
- **Data:** `data/part6_table.csv`
- **Snapshots after each round:** `data/part6a` to `data/part6f`

---

## 2. Final design (deliverable a)

**Final design: D41_D37_dl1_8way**, config file `configs/final_design.cfg`

### Cost, line by line

| Component | Setting | Cost |
|---|---|---|
| Width | W = 8 (ifqsize, decode, issue, commit, ialu = 8; memport = 4) | 32.00 |
| RUU | 32 entries, LSQ 16 | 8.00 |
| L1 I-cache | `il1:8:128:16:l` (16 KB, 16-way, 128 B blocks) | 16.00 |
| L1 D-cache | `dl1:16:32:8:l` (4 KB, 8-way, 32 B blocks) | 4.00 |
| L2 | `ul2:128:128:16:l` (256 KB, 16-way, 128 B blocks) | 32.00 |
| Branch predictor | combined (`-bpred comb -bpred:comb 1024`) | 6.00 |
| Issue mode | out-of-order | 0.00 |
| **Total** | | **98.00** (budget 100) |

### Final vs default

| | Default (D01, cost 86) | Final (D41, cost 98) | Change |
|---|---|---|---|
| IPC compress95 | 1.7145 | 2.1831 | +27.3% |
| IPC cc1 | 0.8849 | 1.3687 | +54.7% |
| **Geometric-mean IPC** | **1.2317** | **1.7286** | **+40.3%** |

### Verification

- The config was re-run through `-config` using `scripts/run_final_cfg.sh`
- It gives the same IPC as the original run (compress95 2.1831, cc1 1.3687)

---

## 3. The path I took (deliverable b)

The search had **six rounds (6a to 6f)**. Each round used what the previous one taught.

### Summary of all rounds

| Round | Designs | Idea | Best design | Cost | gm | vs default |
|---|---|---|---|---|---|---|
| 6a | D01 to D12 | Broad ideas from Parts 2 to 5 | D03 | 94 | 1.4797 | +20.1% |
| 6b | D13 to D20 | Find out why D03 won, free tweaks | D18 | 94 | 1.5160 | +23.1% |
| 6c | D21 to D25 | Stack the winners on D18 | D21 | 94 | 1.5302 | +24.2% |
| 6d | D26 to D33 | Try to beat D21 | D26 | 98 | 1.5549 | +26.2% |
| 6e | D34 to D38 | Build on D26 | D37 | 98 | 1.7248 | +40.0% |
| 6f | D39 to D43 | Confirm convergence | D41 | 98 | 1.7286 | +40.3% |

### Progress of the best design

| After round | Design | Cost | compress95 | cc1 | gm |
|---|---|---|---|---|---|
| default | D01 | 86 | 1.7145 | 0.8849 | 1.2317 |
| 6a | D03 | 94 | 1.9227 | 1.1387 | 1.4797 |
| 6b | D18 | 94 | 1.8984 | 1.2106 | 1.5160 |
| 6c | D21 | 94 | 1.9029 | 1.2305 | 1.5302 |
| 6d | D26 | 98 | 1.9189 | 1.2599 | 1.5549 |
| 6e | D37 | 98 | 2.1790 | 1.3652 | 1.7248 |
| 6f | D41 | 98 | 2.1831 | 1.3687 | 1.7286 |

---

### Round 6a: broad ideas (D01 to D12)

- Tested one idea per design from Parts 2 to 5: bigger window plus combined predictor, free I-cache reorganisation, bigger L1 caches paid for by a smaller L2, width 8, no L2, cheap width-2 machine
- Best: **D03** (cost 94, gm 1.4797, +20.1%). Same 16 KB I-cache as the default but 4-way with 64 B blocks, which costs nothing extra
- cc1 rose from 0.931 (D02) to 1.139 (+22.3%); compress95 did not change
- The L2 is very valuable: cutting it to 128 KB or less (D04, D08, D12) lost performance, and removing it (D09, gm 1.1236) was worse than the default
- Width 8 with a small L2 (D06, D07) lost to D03
- Lesson: cc1 is limited by instruction-cache misses, and the cost model charges only for cache size, so associativity and block size are free

### Round 6b: why did D03 win? (D13 to D20)

- Split D03's change in two: D13 (direct-mapped, 64 B blocks) and D14 (4-way, 32 B blocks)
- cc1 IPC: D02 0.931, D14 1.006, D13 1.085, D03 1.139. Both changes help; longer blocks help more (spatial locality in sequential fetch) and associativity removes conflict misses
- Best: **D18** (128 B blocks in I-cache and L2), gm 1.5160, +2.5% over D03. cc1 rose to 1.211; compress95 fell 1.3% (longer miss penalty)
- Free tweaks: 8-way L2 (D17) +0.4%, 8-way I-cache (D15) +0.2%, 64 B D-blocks (D16) no gain
- Trade-offs: 8 KB D-cache with RUU 64 (D19) no gain; W=8 with the full L2 (D20, cost 98) scored 1.5029, so width 8 only works if the L2 is kept

### Round 6c: stack the winners on D18 (D21 to D25)

- Best: **D21** (D18 plus 8-way I-cache and 8-way L2), gm 1.5302, +24.2%, cost 94, no extra cost
- 64 B D-blocks (D22, 1.5157) and RUU 64 with 8 KB D-cache (D23, 1.5156) did not beat D18
- 32 KB I-cache with 128 KB L2 (D24, 1.3991) was worse
- 256 B blocks (D25, 1.4982) were worse than 128 B, so 128 B is the best block size

### Round 6d: try to beat D21 (D26 to D33)

- Best: **D26** (W=8, RUU 16, 8 KB D-cache, D21 caches, cost 98), gm 1.5549, +1.6% over D21. Width 8 now pays because the cache organisation is good and the L2 is intact
- 16-way I-cache and L2 (D32, free): 1.5359, +0.4% over D21
- 8 KB D-cache (D27, cost 86): 1.5130, only 1.1% below D21, so the D-cache is cheap to shrink
- RUU 64 (D28) equal to D21; smaller L2 (D29) and 256 B L2 blocks (D31) lost
- Problem: the first D29, D30 and D33 used 5-way and 6-way caches, which sim-outorder rejected. Failed runs left empty files, which were deleted. D29 and D33 were redone with power-of-two sizes; D30 was dropped (over budget)

### Round 6e: build on D26 (D34 to D38)

- Added 16-way caches to D26 and moved units from the D-cache to the RUU
- Best: **D37** (W=8, RUU 32, 4 KB D-cache, 16-way I-cache and L2), gm 1.7248, +40.0%. Largest single jump of the search (+10.5% over D34)
- The jump came from the window, not the D-cache: D26 (8 KB, RUU 16) 1.5549, D36 (4 KB, RUU 16) 1.5244, D35 (4 KB, RUU 32) 1.7175
- At width 8 a 16-entry window cannot expose enough parallelism (Part 2 showed a similar effect)
- 16-way caches alone (D34): +0.4%; 2-way D-cache (D38) was worse than 4-way

### Round 6f: confirm convergence (D39 to D43)

- Best: **D41** (D37 with an 8-way 4 KB D-cache, free), gm 1.7286, +0.2% over D37
- D39 (RUU 64, 8 KB I-cache): compress95 +4.8%, cc1 -4.6%, so gm flat at 1.7247
- D40 (RUU 64, 128 KB L2, cost 90): 1.6051; D43 (RUU 128, small caches): 1.5881; 64 B D-blocks (D42) slightly worse
- Four designs were within 0.4% of each other and the 2 spare units cannot buy any legal upgrade, so the search stopped. D41 is final

### Key candidates

| Design | Description | Cost | compress95 | cc1 | gm |
|---|---|---|---|---|---|
| D01 | default | 86 | 1.7145 | 0.8849 | 1.2317 |
| D02 | RUU 32 + comb | 94 | 1.9172 | 0.9307 | 1.3358 |
| D03 | I-cache 4-way, 64 B | 94 | 1.9227 | 1.1387 | 1.4797 |
| D09 | no L2 | 94 | 1.6552 | 0.7628 | 1.1236 |
| D11 | W=2 | 58 | 1.1020 | 0.6389 | 0.8391 |
| D13 | I-cache direct-mapped, 64 B | 94 | 1.9186 | 1.0846 | 1.4425 |
| D14 | I-cache 4-way, 32 B | 94 | 1.9229 | 1.0060 | 1.3908 |
| D18 | 128 B blocks | 94 | 1.8984 | 1.2106 | 1.5160 |
| D21 | D18 + 8-way I-cache and L2 | 94 | 1.9029 | 1.2305 | 1.5302 |
| D26 | W=8, RUU 16, 8 KB D-cache | 98 | 1.9189 | 1.2599 | 1.5549 |
| D35 | W=8, RUU 32, 4 KB D-cache | 98 | 2.1742 | 1.3568 | 1.7175 |
| D36 | W=8, RUU 16, 4 KB D-cache | 94 | 1.8813 | 1.2352 | 1.5244 |
| D37 | D35 + 16-way caches | 98 | 2.1790 | 1.3652 | 1.7248 |
| D39 | RUU 64, 8 KB I-cache | 98 | 2.2837 | 1.3025 | 1.7247 |
| D40 | RUU 64, 128 KB L2 | 90 | 2.0081 | 1.2830 | 1.6051 |
| D41 | **final** (8-way D-cache) | 98 | 2.1831 | 1.3687 | 1.7286 |
| D43 | RUU 128, small caches | 98 | 2.0910 | 1.2062 | 1.5881 |

All 42 designs: `data/part6_table.csv`

---

### Graphs

**Graph 1: IPC vs cost** (`data/part6_g1_scatter.png`)
- Shows geometric-mean IPC against cost for every design
- The default sits at (86, 1.23)
- Most 94-unit designs lie between 1.31 and 1.54
- The 98-unit designs form two groups: about 1.5 to 1.56 (RUU 16) and 1.72 to 1.73 (W=8, RUU 32)
- Up and to the left is better; D11 (58 units) shows how fast IPC drops when spending less

**Graph 2: IPC of every design** (`data/part6_g2_bars.png`)
- cc1 gains most from cache organisation (0.885 to 1.369)
- compress95 gains most from width and window (1.71 to 2.18)
- The geometric mean rewards percentage gains equally on both benchmarks

**Graph 3: final vs default** (`data/part6_g3_final_vs_default.png`)
- compress95 +27.3%, cc1 +54.7%, gm +40.3%

**Graph 4: cost breakdown** (`data/part6_g4_cost_breakdown.png`)
- Default: 32 on the L2, 16 each on width and the two L1 caches
- Final: 32 on width, 32 on the L2, 16 on the I-cache, 8 on the RUU, 4 on the D-cache
- Budget moved from the D-cache and window to width and a better-organised I-cache

---

## 4. Justification (deliverable c)

### Where the budget went
- Width 8: 32 units
- 256 KB L2: 32 units
- 16 KB I-cache: 16 units
- 32-entry RUU: 8 units
- 4 KB D-cache: 4 units
- Combined predictor: 6 units
- Total 98 of 100; the 2 spare units cannot buy any legal upgrade (every component grows in steps of 4 or more)

### Free changes first (Part 4)
- cc1 suffers from instruction-cache misses (80.8 per 1000 instructions)
- Removing the L2 slows cc1 by up to 9.3 times
- The cost model charges only for capacity, so we changed organisation at no cost: 4-way, 8-way, 16-way and 128 B blocks
- This took cc1 from 0.885 to about 1.24 (D32) before spending any units: the best gain per unit in the design
- Block size has a limit: 256 B blocks (D25) were worse than 128 B

### Keep the L2 (Part 4)
- The L2 reduced the cost of memory latency by about 13 times (compress95) and 21 times (cc1)
- It costs 0.125 per KB, 8 times less than an L1
- Every design that cut or removed the L2 lost (D04, D08, D09, D12, D24, D29, D40)

### Width 8 only with a big enough window (Parts 2 and 3)
- Part 2: width alone is poorly used (cc1 reached only 1.03 IPC at W=8 on default caches)
- Early W=8 designs (D06, D07, D08) lost because they cut the L2 to pay for width
- Once the caches were fixed (D26), W=8 was worth its 16 extra units
- Part 3: RUU size gave small gains at W=4, but at W=8 a 16-entry window is a bottleneck
- RUU 16 to 32 gave +10% (D36 to D35)
- RUU 64 and 128 gave nothing in gm, because the caches they displaced were worth more (D39, D40, D43)

### Combined predictor (Part 5)
- +7.6% IPC on compress95 and +1.7% on cc1 over bimodal
- It costs 6 units, and a wider machine loses more to mispredictions
- Kept in every design after D01

### What was given up
- D-cache cut from 16 KB to 4 KB: small cost (8 KB D-cache was only -1.1% in D27) because the L2 catches most misses
- Those 12 units paid for the window and width
- I-cache stayed at 16 KB: enlarging it required shrinking the L2, which lost (D04, D24)
- RUU is only 32 entries

### Trade-off between benchmarks
- compress95 gained 27.3% and cc1 54.7%
- Cache organisation was cheapest for cc1; width and window for compress95
- D39 shows the limit: compress95 +4.8% but cc1 -4.6%, so no gain in gm

---

## 5. Observations and problems

- sim-outorder rejected 5-way and 6-way caches (associativity must be a power of 2), so D29, D30 and D33 were redone or dropped
- Failed runs left empty output files, which were deleted before re-running
- The search stopped after 6f: the last round gained only 0.2% and the 2 remaining units buy nothing
- This is a local optimum, not a proven global one
- Simulations are deterministic, so small differences are real, but they apply only to these two benchmarks with the 100M-instruction cap