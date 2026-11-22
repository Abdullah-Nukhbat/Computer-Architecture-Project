#!/bin/bash
# re-runs the final design through -config (what the TA will do)
cd /mnt/d/CA_Project/BenchMarks_Little/Input || exit 1
env -i /mnt/d/CA_Project/simplesim-3.0/sim-outorder -config /mnt/d/CA_Project/configs/final_design.cfg -redir:sim /mnt/d/CA_Project/results/compress95_P6v_final_cfg.txt ../Programs/compress95.ss < compress95.in > /dev/null
env -i /mnt/d/CA_Project/simplesim-3.0/sim-outorder -config /mnt/d/CA_Project/configs/final_design.cfg -redir:sim /mnt/d/CA_Project/results/cc1_P6v_final_cfg.txt ../Programs/cc1.ss -O 1stmt.i > /dev/null
grep "^sim_IPC" /mnt/d/CA_Project/results/compress95_P6v_final_cfg.txt /mnt/d/CA_Project/results/cc1_P6v_final_cfg.txt
grep "^sim_IPC" /mnt/d/CA_Project/results/compress95_P6_D03_il1_free.txt /mnt/d/CA_Project/results/cc1_P6_D03_il1_free.txt
