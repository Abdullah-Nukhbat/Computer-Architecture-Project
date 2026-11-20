#!/bin/bash
# Part 4: memory hierarchy. 32 required runs + 4 extra (P4x). Safe to re-run.
ROOT=/mnt/d/CA_Project
SIM=$ROOT/simplesim-3.0/sim-outorder
RES=$ROOT/results
cd $ROOT/BenchMarks_Little/Input || exit 1
CAP="-max:inst 100000000"

run_bench () {
  NAME=$1; OPTS=$2; TAG=$3
  OUT=$RES/${NAME}_${TAG}.txt
  if grep -q "^sim_IPC" $OUT 2>/dev/null; then return; fi
  echo "running $NAME $TAG"
  if [ "$NAME" = "compress95" ]; then
    env -i $SIM $OPTS -redir:sim $OUT ../Programs/compress95.ss < compress95.in > /dev/null
  else
    env -i $SIM $OPTS -redir:sim $OUT ../Programs/cc1.ss -O 1stmt.i
  fi
}

both () { run_bench compress95 "$1" "$2"; run_bench cc1 "$1" "$2"; }

# (a) L1 data-cache capacity: 4-way, 32 B blocks, sets = KB*8
for K in 1 4 16 64; do
  S=$((K * 8))
  both "$CAP -cache:dl1 dl1:${S}:32:4:l" P4a_dl1_${K}KB
done

# (b) L1 data-cache block size: 16 KB, 4-way, sets = 4096/B
for B in 8 16 32 64; do
  S=$((4096 / B))
  both "$CAP -cache:dl1 dl1:${S}:${B}:4:l" P4b_blk${B}B
done

# (c) memory latency, with and without L2
for L in 25 50 100 200; do
  both "$CAP -mem:lat $L 2" P4c_lat${L}_L2
  both "$CAP -mem:lat $L 2 -cache:dl2 none -cache:il2 none" P4c_lat${L}_noL2
done

# extra (3C classification): 16 KB direct-mapped and 16 KB 16-way
both "$CAP -cache:dl1 dl1:512:32:1:l" P4x_dl1_16KB_1way
both "$CAP -cache:dl1 dl1:32:32:16:l" P4x_dl1_16KB_16way

echo "all done"
