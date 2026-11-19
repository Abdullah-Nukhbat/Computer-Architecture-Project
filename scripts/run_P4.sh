#!/bin/bash
# Part 4: memory hierarchy, 16 configurations x 2 benchmarks = 32 runs.
# Safe to re-run: finished runs are skipped.
source "$(dirname "$0")/common.sh"

# (a) L1 data-cache capacity: 4-way, 32-byte blocks, LRU
run_both P4a_dl1_1KB  -cache:dl1 dl1:8:32:4:l
run_both P4a_dl1_4KB  -cache:dl1 dl1:32:32:4:l
run_both P4a_dl1_16KB -cache:dl1 dl1:128:32:4:l     # default
run_both P4a_dl1_64KB -cache:dl1 dl1:512:32:4:l

# (b) L1 data-cache block size: 16 KB, 4-way, LRU
run_both P4b_blk8  -cache:dl1 dl1:512:8:4:l
run_both P4b_blk16 -cache:dl1 dl1:256:16:4:l
run_both P4b_blk32 -cache:dl1 dl1:128:32:4:l        # default
run_both P4b_blk64 -cache:dl1 dl1:64:64:4:l

# (c) main-memory latency, with the default L2 and with no L2
for LAT in 25 50 100 200; do
  run_both P4c_lat${LAT}_L2   -mem:lat $LAT 2
  run_both P4c_lat${LAT}_noL2 -mem:lat $LAT 2 -cache:dl2 none -cache:il2 none
done

wait
echo "all done"
