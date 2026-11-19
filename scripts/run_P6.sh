#!/bin/bash
# Part 6: run every candidate design in scripts/p6_designs.py on both
# benchmarks. Designs over the 100-unit budget are never run.
# Safe to re-run: finished designs are skipped.
source "$(dirname "$0")/common.sh"

while IFS='|' read -r NAME OPTS; do
  run_both "P6_$NAME" $OPTS
done < <(python3 "$REPO/scripts/p6_designs.py" --run-list)

wait
echo "all done"

# Final design as a full configuration file, for re-running with -config
mkdir -p "$REPO/configs"
"$SIM" -max:inst 100000000 $(python3 "$REPO/scripts/p6_designs.py" --final-options) \
  -dumpconfig "$REPO/configs/P6_final.cfg"
echo "wrote configs/P6_final.cfg"
