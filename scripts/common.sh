# Shared helpers for run_P4.sh, run_P5.sh and run_P6.sh.
# Loads paths from .env, then runs simulations in parallel.
# Set JOBS to change how many run at once (default: CPU cores - 2).

source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$BENCH/Input" || exit 1

JOBS=${JOBS:-$(( $(nproc) > 2 ? $(nproc) - 2 : 1 ))}
CAP="-max:inst 100000000"

# run_bench <benchmark> <tag> <options...>
# Saves the statistics to $RES/<benchmark>_<tag>.txt.
# Skips runs that already finished, so a script can safely be re-run.
run_bench () {
  local NAME=$1 TAG=$2; shift 2
  local OUT="$RES/${NAME}_${TAG}.txt"
  if grep -q "^sim_IPC" "$OUT" 2>/dev/null; then return; fi
  while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n; done
  echo "running $NAME $TAG"
  if [ "$NAME" = "compress95" ]; then
    env -i "$SIM" $CAP "$@" -redir:sim "$OUT" ../Programs/compress95.ss < compress95.in > /dev/null &
  else
    # cc1 writes 1stmt.s here; only its statistics are used after Part 1
    env -i "$SIM" $CAP "$@" -redir:sim "$OUT" ../Programs/cc1.ss -O 1stmt.i 2>/dev/null &
  fi
}

# run_both <tag> <options...>   runs the same configuration on both benchmarks
run_both () {
  local TAG=$1; shift
  run_bench compress95 "$TAG" "$@"
  run_bench cc1 "$TAG" "$@"
}
