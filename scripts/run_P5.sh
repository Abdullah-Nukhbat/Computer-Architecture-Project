#!/bin/bash
# Part 5: branch prediction, 6 predictors x 2 benchmarks = 12 runs.
# Safe to re-run: finished runs are skipped.
source "$(dirname "$0")/common.sh"

run_both P5_perfect  -bpred perfect
run_both P5_nottaken -bpred nottaken
run_both P5_bimod512  -bpred bimod -bpred:bimod 512
run_both P5_bimod2048 -bpred bimod -bpred:bimod 2048   # default
run_both P5_2lev     -bpred 2lev -bpred:2lev 1 1024 8 0
run_both P5_comb     -bpred comb -bpred:comb 1024

wait
echo "all done"
