Group number G: 8
(G-1) mod 6 = 1
Benchmark A: compress95
Benchmark B: cc1
Simulator: /mnt/d/CA_Project/simplesim-3.0/sim-outorder
Run from:  /mnt/d/CA_Project/BenchMarks_Little/Input
Cap for Parts 2-6: -max:inst 100000000   (Part 1: NO cap)
Naming: <bench>_P<part>_<param><value>.txt

compress95: env -i $SIM [options] -redir:sim compress95.txt ../Programs/compress95.ss < compress95.in > compress95.out
cc1:        env -i $SIM [options] -redir:sim cc1.txt ../Programs/cc1.ss -O 1stmt.i    (writes 1stmt.s)