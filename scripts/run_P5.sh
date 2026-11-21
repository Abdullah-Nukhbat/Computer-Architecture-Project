#!/bin/bash
# Part 5: branch predictors. 12 required runs + 8 extra (P5x). Safe to re-run.
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

# the six required predictors
both "$CAP -bpred perfect"                          P5_perfect
both "$CAP -bpred nottaken"                         P5_nottaken
both "$CAP -bpred bimod -bpred:bimod 512"           P5_bimod512
both "$CAP -bpred bimod -bpred:bimod 2048"          P5_bimod2048
both "$CAP -bpred 2lev -bpred:2lev 1 1024 8 0"      P5_2lev
both "$CAP -bpred comb -bpred:comb 1024"            P5_comb

# extra (question d): perfect predictor at each Part 2 width (RUU 64, LSQ 32)
for CFG in "1 1" "2 1" "4 2" "8 4"; do
  set -- $CFG
  W=$1; MP=$2
  both "$CAP -fetch:ifqsize $W -decode:width $W -issue:width $W -commit:width $W -res:ialu $W -res:memport $MP -ruu:size 64 -lsq:size 32 -bpred perfect" P5x_W${W}_perfect
done

echo "all done"