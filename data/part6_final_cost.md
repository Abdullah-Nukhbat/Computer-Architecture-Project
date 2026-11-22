# Final design D41_D37_dl1_8way

| Component | Cost |
|---|---|
| Width W=8 (4 per unit of W) | 32.00 |
| RUU 32 entries, LSQ 16 (0.25 per entry) | 8.00 |
| L1 I-cache 16 KB (1 per KB) | 16.00 |
| L1 D-cache 4 KB (1 per KB) | 4.00 |
| L2 256 KB (0.125 per KB) | 32.00 |
| Branch predictor comb | 6.00 |
| **Total** | **98.00** (budget 100) |

| | default | final |
|---|---|---|
| IPC compress95 | 1.7145 | 2.1831 |
| IPC cc1 | 0.8849 | 1.3687 |
| Geometric-mean IPC | 1.2317 | 1.7286 |
