# Final design D21_D18_8way

| Component | Cost |
|---|---|
| Width W=4 (4 per unit of W) | 16.00 |
| RUU 32 entries, LSQ 16 (0.25 per entry) | 8.00 |
| L1 I-cache 16 KB (1 per KB) | 16.00 |
| L1 D-cache 16 KB (1 per KB) | 16.00 |
| L2 256 KB (0.125 per KB) | 32.00 |
| Branch predictor comb | 6.00 |
| **Total** | **94.00** (budget 100) |

| | default | final |
|---|---|---|
| IPC compress95 | 1.7145 | 1.9029 |
| IPC cc1 | 0.8849 | 1.2305 |
| Geometric-mean IPC | 1.2317 | 1.5302 |
