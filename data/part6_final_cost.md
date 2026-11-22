# Final design D26_W8_D21tweaks

| Component | Cost |
|---|---|
| Width W=8 (4 per unit of W) | 32.00 |
| RUU 16 entries, LSQ 8 (0.25 per entry) | 4.00 |
| L1 I-cache 16 KB (1 per KB) | 16.00 |
| L1 D-cache 8 KB (1 per KB) | 8.00 |
| L2 256 KB (0.125 per KB) | 32.00 |
| Branch predictor comb | 6.00 |
| **Total** | **98.00** (budget 100) |

| | default | final |
|---|---|---|
| IPC compress95 | 1.7145 | 1.9189 |
| IPC cc1 | 0.8849 | 1.2599 |
| Geometric-mean IPC | 1.2317 | 1.5549 |
