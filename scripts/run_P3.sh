#!/bin/bash
# Part 3: RUU size sweep (12 runs) + 2 extra runs for question (c).
# Safe to re-run: finished runs are skipped.
source "$(dirname "$0")/env.sh"   # reads SIM, BENCH, RES from .env
cd "$BENCH/Input" || exit 1

run_bench () {
  NAME=$1; OPTS=$2; TAG=$3
  OUT="$RES/${NAME}_${TAG}.txt"
  if grep -q "^sim_IPC" "$OUT" 2>/dev/null; then return; fi
  echo "running $NAME $TAG"
  if [ "$NAME" = "compress95" ]; then
    env -i "$SIM" $OPTS -redir:sim "$OUT" ../Programs/compress95.ss < compress95.in > /dev/null
  else
    env -i "$SIM" $OPTS -redir:sim "$OUT" ../Programs/cc1.ss -O 1stmt.i
  fi
}

# Main sweep: default width 4, LSQ = RUU / 2
for R in 4 8 16 32 64 128; do
  L=$((R / 2))
  OPTS="-max:inst 100000000 -ruu:size $R -lsq:size $L"
  run_bench compress95 "$OPTS" P3_ruu$R
  run_bench cc1        "$OPTS" P3_ruu$R
done

# Extra runs for question (c): W=8 with a 16-entry RUU (LSQ 8)
OPTS8="-max:inst 100000000 -fetch:ifqsize 8 -decode:width 8 -issue:width 8 -commit:width 8 -res:ialu 8 -res:memport 4 -ruu:size 16 -lsq:size 8"
run_bench compress95 "$OPTS8" P3c_W8_ruu16
run_bench cc1        "$OPTS8" P3c_W8_ruu16

echo "all done"