#!/bin/bash
source "$(dirname "$0")/env.sh"   # reads SIM, BENCH, RES from .env
cd "$BENCH/Input" || exit 1

# compress95 (full run, no -max:inst)
env -i "$SIM" -redir:sim "$RES/compress95_P1.txt" ../Programs/compress95.ss < compress95.in > "$RES/compress95_P1.out"

# cc1 (delete the stale output first)
rm -f 1stmt.s
env -i "$SIM" -redir:sim "$RES/cc1_P1.txt" ../Programs/cc1.ss -O 1stmt.i
cp 1stmt.s "$RES/cc1_P1_1stmt.s"

# verification: empty output under each heading = identical = correct
echo "== diff compress95 ==" | tee "$RES/P1_diff.txt"
diff "$RES/compress95_P1.out" ../Expected_Output/compress95.out | tee -a "$RES/P1_diff.txt"
echo "== diff cc1 ==" | tee -a "$RES/P1_diff.txt"
diff "$RES/cc1_P1_1stmt.s" ../Expected_Output/1stmt.s | tee -a "$RES/P1_diff.txt"
echo "done"