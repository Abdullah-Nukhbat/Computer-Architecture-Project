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
