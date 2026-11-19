# Computer Architecture Project

## Setup on a new machine

1. Build the simulator (`git clone https://github.com/toddmaustin/simplesim-3.0`, then `make config-pisa && make sim-outorder`).
   On newer Linux, if the build stops at `termio.h: No such file or directory`, change that line in `syscall.c` to `#include <termios.h>`.
2. Get `BenchMarks_Little/` from https://github.com/priyankarroychowdhury3/Simplescalar.
3. Tell the scripts where those are:

       cp .env.example .env    # then edit SIM and BENCH in .env

4. Run a part and draw its graphs, from anywhere:

       bash scripts/run_P2.sh
       python3 scripts/part2_graphs.py

`.env` is git-ignored, so everyone keeps their own paths. Results go to `results/`, graphs and CSVs to `data/`.

## Scripts per part

| Part | Run | Graphs and tables | Notes |
|---|---|---|---|
| 1 | `scripts/run_P1.sh` | `part1_table.py`, `part1_extra_charts.py` | full runs, no `-max:inst` |
| 2 | `scripts/run_P2.sh` | `part2_graphs.py` | |
| 3 | `scripts/run_P3.sh` | `part3_graphs.py` | |
| 4 | `scripts/run_P4.sh`, `scripts/run_P4_3c.sh` | `part4_graphs.py` | `run_P4_3c.sh` = extra runs for the 3C split |
| 5 | `scripts/run_P5.sh` | `part5_graphs.py` | |
| 6 | `scripts/run_P6.sh` | `part6_graphs.py` | designs and cost model in `p6_designs.py`; final config in `configs/P6_final.cfg` |
| all | | `all_runs_csv.py` | one row per run in `data/all_runs.csv` |

Parts 4-6 run several simulations at once (CPU cores - 2 by default; set
`JOBS=4 bash scripts/run_P4.sh` to use fewer). Finished runs are skipped, so a
script can be re-run safely after an interruption.
