#!/bin/bash
# Part 4 extra runs for question (a), classifying misses into the 3 Cs.
#   compulsory ~ misses of a huge cache (nothing is ever evicted)
#   capacity   ~ misses of a fully-associative cache of the same size,
#                minus compulsory (no conflicts are possible)
#   conflict   = misses of the real 4-way cache - fully-associative misses
# Fully associative = 1 set with all blocks in it.
source "$(dirname "$0")/common.sh"

run_both P4x_dl1_1KB_full  -cache:dl1 dl1:1:32:32:l
run_both P4x_dl1_4KB_full  -cache:dl1 dl1:1:32:128:l
run_both P4x_dl1_16KB_full -cache:dl1 dl1:1:32:512:l
run_both P4x_dl1_64KB_full -cache:dl1 dl1:1:32:2048:l
run_both P4x_dl1_4MB       -cache:dl1 dl1:32768:32:4:l

wait
echo "all done"
