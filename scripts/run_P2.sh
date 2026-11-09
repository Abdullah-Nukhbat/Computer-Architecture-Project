#!/bin/bash
# Part 2: width sweep, 16 runs. Safe to re-run: finished runs are skipped.
ROOT=/mnt/d/CA_Project
SIM=$ROOT/simplesim-3.0/sim-outorder
RES=$ROOT/results
cd $ROOT/BenchMarks_Little/Input || exit 1

run_one () {
  W=$1; MP=$2; MODE=$3
  EXTRA=""
  if [ "$MODE" = "inorder" ]; then EXTRA="-issue:inorder true"; fi
  OPTS="-max:inst 100000000 -fetch:ifqsize $W -decode:width $W -issue:width $W -commit:width $W -res:ialu $W -res:memport $MP -ruu:size 64 -lsq:size 32 $EXTRA"

  OUT=$RES/compress95_P2_W${W}_${MODE}.txt
  if ! grep -q "^sim_IPC" $OUT 2>/dev/null; then
    echo "running compress95 W=$W $MODE"
    env -i $SIM $OPTS -redir:sim $OUT ../Programs/compress95.ss < compress95.in > /dev/null
  fi

  OUT=$RES/cc1_P2_W${W}_${MODE}.txt
  if ! grep -q "^sim_IPC" $OUT 2>/dev/null; then
    echo "running cc1 W=$W $MODE"
    env -i $SIM $OPTS -redir:sim $OUT ../Programs/cc1.ss -O 1stmt.i
  fi
}

for MODE in ooo inorder; do
  run_one 1 1 $MODE
  run_one 2 1 $MODE
  run_one 4 2 $MODE
  run_one 8 4 $MODE
done
echo "all done"