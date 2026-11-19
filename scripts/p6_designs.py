"""Part 6: candidate processor designs and the cost model.

Each design lists only what it changes. Everything else stays at the
sim-outorder default (memory latency, cache latencies, imult, FP units, BTB,
RAS), as the rules require. Cost model from the project statement:

  width W            4 per W   (ifqsize = decode = issue = commit = ialu = W,
                                memport = max(1, W/2))
  RUU                0.25 per entry (LSQ = RUU / 2)
  L1 I-cache         1 per KB
  L1 D-cache         1 per KB
  unified L2         0.125 per KB (or none)
  branch predictor   nottaken 0, bimod 1 per 1024 entries,
                     2lev 1 1024 8 0: 3, comb (default sizes): 6
Budget: 100 units.

Run "python3 scripts/p6_designs.py" to print every design's cost.
"""

BUDGET = 100
FINAL = "D24_D17_l2_16way"   # best geometric-mean IPC within budget

DEFAULT = dict(W=4, ruu=16, il1="il1:512:32:1:l", dl1="dl1:128:32:4:l",
               l2="ul2:1024:64:4:l", bpred="bimod", bimod=2048, inorder=False)

# name -> changes from DEFAULT.  Stage 1 explores; stage 2 refines the best.
DESIGNS = {
    # ---- stage 1: one idea at a time, starting from the default
    "D00_default":         {},
    "D01_comb":            dict(bpred="comb"),
    "D02_ruu64":           dict(ruu=64),
    "D03_il1_4way":        dict(il1="il1:128:32:4:l"),
    "D04_W8_ruu32_l2_128": dict(W=8, ruu=32, l2="ul2:512:64:4:l"),
    "D05_ruu32_comb":      dict(ruu=32, bpred="comb"),
    "D06_noL2_il1_32":     dict(ruu=64, il1="il1:256:32:4:l", l2=None, bpred="comb"),

    # ---- stage 2: combine the winners (W=8, 4-way il1, comb) and find
    #      where to take the units from (L2 size, dl1 size, RUU)
    "D07_W8_r32_il4w_l2_128_comb": dict(W=8, ruu=32, il1="il1:128:32:4:l",
                                        l2="ul2:512:64:4:l", bpred="comb"),
    "D08_W8_r64_il4w_l2_64_comb":  dict(W=8, ruu=64, il1="il1:128:32:4:l",
                                        l2="ul2:256:64:4:l", bpred="comb"),
    "D09_W8_r64_il4w_dl8_comb":    dict(W=8, ruu=64, il1="il1:128:32:4:l",
                                        dl1="dl1:64:32:4:l", l2="ul2:512:64:4:l", bpred="comb"),
    "D10_W8_r32_8way_all_comb":    dict(W=8, ruu=32, il1="il1:64:32:8:l",
                                        dl1="dl1:64:32:8:l", l2="ul2:256:64:8:l", bpred="comb"),
    "D11_W8_r32_il32_dl8_l2_64":   dict(W=8, ruu=32, il1="il1:256:32:4:l",
                                        dl1="dl1:64:32:4:l", l2="ul2:256:64:4:l", bpred="comb"),
    "D12_W8_r64_il4w_l2_128_bim":  dict(W=8, ruu=64, il1="il1:128:32:4:l",
                                        l2="ul2:512:64:4:l"),
    "D13_W8_r32_il4w_l2_128_b8k":  dict(W=8, ruu=32, il1="il1:128:32:4:l",
                                        l2="ul2:512:64:4:l", bimod=8192),
    "D14_W4_r64_il4w":             dict(ruu=64, il1="il1:128:32:4:l"),
    "D15_W8_r64_il4w_l2_32_comb":  dict(W=8, ruu=64, il1="il1:128:32:4:l",
                                        l2="ul2:128:64:4:l", bpred="comb"),

    # ---- stage 3: merge D09 (RUU 64, 8 KB dl1) with D10 (8-way caches),
    #      then try the free knobs: associativity and block size
    "D16_W8_r64_8way_dl8_comb":    dict(W=8, ruu=64, il1="il1:64:32:8:l",
                                        dl1="dl1:32:32:8:l", l2="ul2:256:64:8:l", bpred="comb"),
    "D17_D16_il1_64B":             dict(W=8, ruu=64, il1="il1:32:64:8:l",
                                        dl1="dl1:32:32:8:l", l2="ul2:256:64:8:l", bpred="comb"),
    "D18_D16_il1_dl1_64B":         dict(W=8, ruu=64, il1="il1:32:64:8:l",
                                        dl1="dl1:16:64:8:l", l2="ul2:256:64:8:l", bpred="comb"),
    "D19_D16_16way":               dict(W=8, ruu=64, il1="il1:32:32:16:l",
                                        dl1="dl1:16:32:16:l", l2="ul2:128:64:16:l", bpred="comb"),
    "D20_D16_bimod4k":             dict(W=8, ruu=64, il1="il1:64:32:8:l",
                                        dl1="dl1:32:32:8:l", l2="ul2:256:64:8:l", bimod=4096),
    "D21_D17_bimod8k":             dict(W=8, ruu=64, il1="il1:32:64:8:l",
                                        dl1="dl1:32:32:8:l", l2="ul2:256:64:8:l", bimod=8192),

    # ---- stage 4: refine around D17 (64 B il1 blocks were the big win)
    "D22_D17_il1_128B_l2_128B":    dict(W=8, ruu=64, il1="il1:16:128:8:l",
                                        dl1="dl1:32:32:8:l", l2="ul2:128:128:8:l", bpred="comb"),
    "D23_D17_il1_16way":           dict(W=8, ruu=64, il1="il1:16:64:16:l",
                                        dl1="dl1:32:32:8:l", l2="ul2:256:64:8:l", bpred="comb"),
    "D24_D17_l2_16way":            dict(W=8, ruu=64, il1="il1:32:64:8:l",
                                        dl1="dl1:32:32:8:l", l2="ul2:128:64:16:l", bpred="comb"),
    "D25_D17_r32_dl16":            dict(W=8, ruu=32, il1="il1:32:64:8:l",
                                        dl1="dl1:64:32:8:l", l2="ul2:256:64:8:l", bpred="comb"),
}


def cache_kb(spec):
    if not spec:
        return 0
    _, nsets, bsize, assoc, _ = spec.split(":")
    return int(nsets) * int(bsize) * int(assoc) / 1024


def full(d):
    cfg = dict(DEFAULT)
    cfg.update(d)
    return cfg


def cost(d):
    c = full(d)
    bp = {"nottaken": 0, "taken": 0, "2lev": 3, "comb": 6}.get(c["bpred"])
    if c["bpred"] == "bimod":
        bp = c["bimod"] / 1024
    parts = {"width": 4 * c["W"], "ruu": 0.25 * c["ruu"],
             "il1": cache_kb(c["il1"]), "dl1": cache_kb(c["dl1"]),
             "l2": 0.125 * cache_kb(c["l2"]), "bpred": bp}
    return sum(parts.values()), parts


def options(d):
    c = full(d)
    W = c["W"]
    o = [f"-fetch:ifqsize {W}", f"-decode:width {W}", f"-issue:width {W}",
         f"-commit:width {W}", f"-res:ialu {W}", f"-res:memport {max(1, W // 2)}",
         f"-ruu:size {c['ruu']}", f"-lsq:size {c['ruu'] // 2}",
         f"-cache:il1 {c['il1']}", f"-cache:dl1 {c['dl1']}"]
    if c["l2"]:
        o += [f"-cache:dl2 {c['l2']}", "-cache:il2 dl2"]
    else:
        o += ["-cache:dl2 none", "-cache:il2 none"]
    o.append(f"-bpred {c['bpred']}")
    if c["bpred"] == "bimod":
        o.append(f"-bpred:bimod {c['bimod']}")
    if c["inorder"]:
        o.append("-issue:inorder true")
    return " ".join(o)


def describe(d):
    c = full(d)

    def cache(spec):
        _, _, bsize, assoc, _ = spec.split(":")
        return f"{cache_kb(spec):g} KB {assoc}-way {bsize} B"
    l2 = f"L2 {cache(c['l2'])}" if c["l2"] else "no L2"
    bp = f"bimod {c['bimod']}" if c["bpred"] == "bimod" else c["bpred"]
    return (f"W={c['W']}, RUU {c['ruu']}, il1 {cache(c['il1'])}, "
            f"dl1 {cache(c['dl1'])}, {l2}, {bp}"
            + (", in-order" if c["inorder"] else ""))


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--final-options"]:
        print(options(DESIGNS[FINAL]))
    elif sys.argv[1:] == ["--run-list"]:
        # used by run_P6.sh: "<name>|<options>" for every design within budget
        for name, d in DESIGNS.items():
            if cost(d)[0] <= BUDGET:
                print(f"{name}|{options(d)}")
    else:
        for name, d in DESIGNS.items():
            total, _ = cost(d)
            flag = "" if total <= BUDGET else "   OVER BUDGET"
            print(f"{name:<26} {total:>6.2f}  {describe(d)}{flag}")
