ROOT = "/mnt/d/CA_Project"
SIM = ROOT + "/simplesim-3.0/sim-outorder"
RES = ROOT + "/results"
INPUT = ROOT + "/BenchMarks_Little/Input"
BENCHES = ["compress95", "cc1"]
BUDGET = 100.0

# cache = (nsets, bsize, assoc)
DEF_IL1 = (512, 32, 1)
DEF_DL1 = (128, 32, 4)
DEF_L2 = (1024, 64, 4)

def D(name, W, ruu, il1, dl1, l2, bp, note):
    return dict(name=name, W=W, ruu=ruu, il1=il1, dl1=dl1, l2=l2, bp=bp, note=note)

# bp is one of: "nottaken", "bimod1024", "bimod2048", "bimod4096", "2lev", "comb"
# l2 = (nsets, bsize, assoc) or None.  The FIRST design must stay the default.
DESIGNS = [
    D("D01_default", 4, 16, DEF_IL1, DEF_DL1, DEF_L2, "bimod2048",
      "reference: default machine"),
    D("D02_ruu32_comb", 4, 32, DEF_IL1, DEF_DL1, DEF_L2, "comb",
      "bigger window + combined predictor (Parts 3 and 5)"),
    D("D03_il1_free", 4, 32, (64, 64, 4), DEF_DL1, DEF_L2, "comb",
      "same 16 KB I-cache but 4-way, 64 B blocks (free in the cost model)"),
    D("D04_il1_32k_halfL2", 4, 32, (256, 32, 4), DEF_DL1, (512, 64, 4), "comb",
      "32 KB I-cache paid for by halving the L2 to 128 KB"),
    D("D05_il1_dl1_blk64", 4, 32, (128, 64, 4), (64, 64, 4), (512, 64, 4), "comb",
      "32 KB 4-way I-cache with 64 B blocks, 64 B D-blocks, 128 KB L2"),
    D("D06_W8_smallL2", 8, 32, (64, 64, 4), DEF_DL1, (256, 64, 4), "comb",
      "width 8, L2 cut to 64 KB"),
    D("D07_W8_ruu64", 8, 64, (64, 64, 4), DEF_DL1, (256, 64, 4), "comb",
      "width 8 with a 64-entry window"),
    D("D08_W8_il1_32k", 8, 32, (128, 64, 4), DEF_DL1, (128, 64, 4), "comb",
      "width 8, 32 KB I-cache, only a 32 KB L2"),
    D("D09_noL2_bigL1", 4, 32, (256, 32, 4), (256, 32, 4), None, "comb",
      "no L2, 32 KB L1s (tests the value of the L2)"),
    D("D10_bigger_dl1", 4, 32, (64, 64, 4), (256, 32, 4), (512, 64, 4), "comb",
      "32 KB D-cache, 128 KB L2"),
    D("D11_W2_cheap", 2, 32, DEF_IL1, DEF_DL1, (256, 64, 4), "bimod2048",
      "cheap low-end design"),
    D("D12_ruu64_il1_32k", 4, 64, (128, 64, 4), DEF_DL1, (256, 64, 4), "comb",
      "bigger window, 32 KB I-cache, 64 KB L2"),
        # ---- 6b: isolate why D03 won (D03 = 4-way I-cache, 64 B blocks)
    D("D13_il1_dm_blk64", 4, 32, (256, 64, 1), DEF_DL1, DEF_L2, "comb",
      "D03 but I-cache direct-mapped: isolates the effect of 64 B blocks"),
    D("D14_il1_4way_blk32", 4, 32, (128, 32, 4), DEF_DL1, DEF_L2, "comb",
      "D03 but I-cache 32 B blocks: isolates the effect of 4-way"),
    # ---- 6b: free tweaks, one change from D03
    D("D15_il1_8way", 4, 32, (32, 64, 8), DEF_DL1, DEF_L2, "comb",
      "D03 but 8-way I-cache (free)"),
    D("D16_dl1_blk64", 4, 32, (64, 64, 4), (64, 64, 4), DEF_L2, "comb",
      "D03 but D-cache 64 B blocks (free)"),
    D("D17_L2_8way", 4, 32, (64, 64, 4), DEF_DL1, (512, 64, 8), "comb",
      "D03 but 8-way L2, same 256 KB (free)"),
    D("D18_blk128_il1_L2", 4, 32, (32, 128, 4), DEF_DL1, (512, 128, 4), "comb",
      "D03 but 128 B blocks in I-cache and L2, same sizes (free)"),
    # ---- 6b: trade units between components
    D("D19_dl1_8k_ruu64", 4, 64, (64, 64, 4), (64, 32, 4), DEF_L2, "comb",
      "D03 but D-cache 8 KB and RUU 64: trades D-cache for window"),
    D("D20_W8_fullL2", 8, 16, (64, 64, 4), (64, 32, 4), DEF_L2, "comb",
      "W=8, RUU 16, D-cache 8 KB, keeps the full 256 KB L2"),
        # ---- 6c: build on D18 (best so far)
    D("D21_D18_8way", 4, 32, (16, 128, 8), DEF_DL1, (256, 128, 8), "comb",
      "D18 + 8-way I-cache + 8-way L2 (free tweaks stacked)"),
    D("D22_D18_dl1_blk", 4, 32, (32, 128, 4), (64, 64, 4), (512, 128, 4), "comb",
      "D18 + 64 B D-cache blocks (tests whether D-blocks now help)"),
    D("D23_D18_ruu64", 4, 64, (32, 128, 4), (64, 32, 4), (512, 128, 4), "comb",
      "D18 but D-cache 8 KB and RUU 64 (D19 idea on D18)"),
    D("D24_D18_il1_32k", 4, 32, (64, 128, 4), DEF_DL1, (256, 128, 4), "comb",
      "D18 + 32 KB I-cache, paid by halving L2 to 128 KB"),
    D("D25_D18_blk256", 4, 32, (16, 256, 4), DEF_DL1, (256, 256, 4), "comb",
      "D18 but 256 B blocks in I-cache and L2 (does the trend continue?)"),
]

# Set to a design name to force the final design; None = best geometric-mean IPC
FINAL_NAME = None

# ---------------- cost model (do not edit) ----------------
def kb(c):
    return c[0] * c[1] * c[2] / 1024.0

def is_pow2(x):
    return x > 0 and (x & (x - 1)) == 0

def bp_ok(bp):
    if bp in ("nottaken", "2lev", "comb"):
        return True
    if bp.startswith("bimod"):
        try:
            n = int(bp[5:])
        except ValueError:
            return False
        return is_pow2(n) and n >= 1024
    return False

def bp_cost(bp):
    if bp == "nottaken": return 0.0
    if bp.startswith("bimod"): return int(bp[5:]) / 1024.0
    if bp == "2lev": return 3.0
    if bp == "comb": return 6.0
    raise ValueError("unknown predictor " + bp)

def cost_lines(dz):
    W, R, l2 = dz["W"], dz["ruu"], dz["l2"]
    return [
        ("Width W=%d (4 per unit of W)" % W, 4.0 * W),
        ("RUU %d entries, LSQ %d (0.25 per entry)" % (R, R // 2), 0.25 * R),
        ("L1 I-cache %g KB (1 per KB)" % kb(dz["il1"]), kb(dz["il1"])),
        ("L1 D-cache %g KB (1 per KB)" % kb(dz["dl1"]), kb(dz["dl1"])),
        ("L2 %s (0.125 per KB)" % ("%g KB" % kb(l2) if l2 else "none"),
         0.125 * kb(l2) if l2 else 0.0),
        ("Branch predictor %s" % dz["bp"], bp_cost(dz["bp"])),
    ]

def cost(dz):
    return sum(c for _, c in cost_lines(dz))

def problems(dz):
    p = []
    if dz["W"] not in (1, 2, 4, 8): p.append("W must be 1, 2, 4 or 8")
    if not is_pow2(dz["ruu"]) or dz["ruu"] < 4: p.append("RUU must be a power of 2, >= 4")
    for k in ("il1", "dl1"):
        c = dz[k]
        if not (is_pow2(c[0]) and is_pow2(c[1]) and c[1] >= 8 and c[2] >= 1):
            p.append(k + " needs power-of-2 sets and block size (>= 8 B)")
    if dz["l2"]:
        c = dz["l2"]
        if not (is_pow2(c[0]) and is_pow2(c[1]) and c[2] >= 1):
            p.append("l2 needs power-of-2 sets and block size")
        for k in ("il1", "dl1"):
            if dz[k][1] > c[1]:
                p.append(k + " block is larger than the L2 block")
    if not bp_ok(dz["bp"]): p.append("predictor not allowed: " + dz["bp"])
    if cost(dz) > BUDGET + 1e-9: p.append("over budget (%.2f > %g)" % (cost(dz), BUDGET))
    return p

def cstr(name, c):
    return "%s:%d:%d:%d:l" % (name, c[0], c[1], c[2])

def options(dz):
    W, R = dz["W"], dz["ruu"]
    o = ["-max:inst", "100000000",
         "-fetch:ifqsize", str(W), "-decode:width", str(W),
         "-issue:width", str(W), "-commit:width", str(W),
         "-res:ialu", str(W), "-res:memport", str(max(1, W // 2)),
         "-ruu:size", str(R), "-lsq:size", str(R // 2),
         "-cache:il1", cstr("il1", dz["il1"]),
         "-cache:dl1", cstr("dl1", dz["dl1"])]
    if dz["l2"]:
        o += ["-cache:dl2", cstr("ul2", dz["l2"])]
    else:
        o += ["-cache:dl2", "none", "-cache:il2", "none"]
    bp = dz["bp"]
    if bp == "nottaken": o += ["-bpred", "nottaken"]
    elif bp == "2lev": o += ["-bpred", "2lev", "-bpred:2lev", "1", "1024", "8", "0"]
    elif bp == "comb": o += ["-bpred", "comb", "-bpred:comb", "1024"]
    else: o += ["-bpred", "bimod", "-bpred:bimod", bp[5:]]
    return o