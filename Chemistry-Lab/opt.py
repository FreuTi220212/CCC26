"""Level-3-Optimierer (Experiment): ILP (Anzahlen + Startbestand, auch nicht kaufbare Molekuele zu Herstellkosten) -> Feuer-Simulation
mit Reparatur-Zukaeufen -> Seeds vorab herstellen -> echte Kosten per Simulation."""
import random
import sys
import time

import numpy as np

FUTURE_PEN = True
ATOMS = True
SKIP_ELEMS = set()


def atom_count(formula):
    import re
    res = {}
    for el, k in re.findall(r'([A-Z][a-z]?)(\d*)', formula):
        res[el] = res.get(el, 0) + (int(k) if k else 1)
    return res
from scipy.optimize import Bounds, LinearConstraint, milp

sys.path.insert(0, 'C:/_repos/CCC26/Chemistry-Lab')
from level2 import parse_reaction, run_case
from level3 import parse, plan_choice, hill_default, unit_costs, hill_climb


def line(rx):
    e, p = rx
    return f"{', '.join(f'{c} {m}' for m, c in e)} -> {', '.join(f'{c} {m}' for m, c in p)}"


def ilp(price, reactions, name, qty, unit, tl, extra_rows=()):
    mols = sorted({m for e, p in reactions for m, _ in e + p} | set(price) | {name})
    mi = {m: i for i, m in enumerate(mols)}
    R, M = len(reactions), len(mols)
    nl = R + M + R
    A = np.zeros((M, nl))
    for r, (e, p) in enumerate(reactions):
        for m, c in e:
            A[mi[m], r] -= c
        for m, c in p:
            A[mi[m], r] += c
    for m in mols:
        A[mi[m], R + mi[m]] = 1
    lo = np.zeros(M)
    lo[mi[name]] = qty
    big = qty * 80 + 80
    rows, rlo = [], []
    cons = [{m for m, _ in e} for e, _ in reactions]
    prod = [{m for m, _ in p} for _, p in reactions]
    for r in range(R):
        row = np.zeros(nl); row[r], row[R + M + r] = -1, big; rows.append(row); rlo.append(0)
        row = np.zeros(nl); row[r], row[R + M + r] = 1, -1; rows.append(row); rlo.append(0)
        for m in cons[r] & prod[r]:  # Katalysator braucht Bestand von aussen
            row = np.zeros(nl)
            row[R + mi[m]] = 1
            for q in range(R):
                if q != r and m in prod[q] and m not in cons[q]:
                    row[R + M + q] = 1
            row[R + M + r] = -1
            rows.append(row); rlo.append(0)
    # Atom-Bedingung: braucht eine Reaktion k Atome eines Elements (z. B. 3 Ti), muessen vorab so viele Atome gekauft sein
    # (Reaktionen erzeugen keine Atome). Erfasst Katalysator-Kreislaeufe (Ti/TiO2, CaO, Fe, Mn, Pt) mit richtiger Startmenge.
    if ATOMS:
        atoms = {m: atom_count(m) for m in mols}
        elems = sorted({el for m in mols for el in atoms[m]})
        for r, (e, p) in enumerate(reactions):
            need = {}
            for m, q in e:
                for el, k in atoms[m].items():
                    need[el] = need.get(el, 0) + k * q
            for el, k in need.items():
                if el in SKIP_ELEMS:
                    continue
                row = np.zeros(nl)
                for m in mols:
                    if atoms[m].get(el):
                        row[R + mi[m]] = atoms[m][el]
                row[R + M + r] = -k
                rows.append(row); rlo.append(0)
    for m, v, r in extra_rows:  # gelernte Startbestaende: benutzt man r, braucht es v Einheiten m vorab
        if m in mi:
            row = np.zeros(nl)
            row[R + mi[m]], row[R + M + r] = 1, -v
            rows.append(row); rlo.append(0)
    cost_s = np.array([float(price[m]) if m in price else float(unit.get(m, 1e6)) for m in mols])
    c = np.concatenate([np.zeros(R), cost_s, np.zeros(R)])
    res = milp(c, constraints=[LinearConstraint(A, lo, np.inf), LinearConstraint(np.array(rows), np.array(rlo), np.inf)],
               integrality=np.ones(nl), bounds=Bounds(np.zeros(nl), np.concatenate([np.full(R + M, np.inf), np.ones(R)])),
               options={"time_limit": tl})
    if res.x is None:
        return None
    count = [int(round(v)) for v in res.x[:R]]
    seed = {m: int(round(res.x[R + mi[m]])) for m in mols if round(res.x[R + mi[m]]) > 0}
    return count, seed, res.fun


def fire(price, reactions, name, qty, count, seed, unit, order):
    R = len(reactions)
    stock, left, out, seed = dict(seed), list(count), [], dict(seed)
    repairs = fire.repairs = []
    while True:
        progress = True
        while progress:
            progress = False
            for r in order:
                while left[r] and all(stock.get(m, 0) >= q for m, q in reactions[r][0]):
                    for m, q in reactions[r][0]:
                        stock[m] -= q
                    for m, q in reactions[r][1]:
                        stock[m] = stock.get(m, 0) + q
                    left[r] -= 1
                    out.append(r)
                    progress = True
        rest = [r for r in range(R) if left[r]]
        if not rest:
            break
        best = None
        future = {}
        for r in rest:
            for m, q in reactions[r][1]:
                future[m] = future.get(m, 0) + q * left[r]
        for r in rest:
            d = {m: q - stock.get(m, 0) for m, q in reactions[r][0] if q > stock.get(m, 0)}
            cst = sum((price[m] if m in price else unit.get(m, 1e6)) * v * (1000 if FUTURE_PEN and future.get(m, 0) - sum(q for o, q in reactions[r][1] if o == m) > 0 else 1)
                      for m, v in d.items())
            if best is None or cst < best[0]:
                best = (cst, d, r)
        for m, v in best[1].items():
            stock[m] = stock.get(m, 0) + v
            seed[m] = seed.get(m, 0) + v
            repairs.append((m, v, best[2]))
    return out, seed


def build(price, reactions, name, qty, out, seed, default):
    pre = []
    for m, v in seed.items():
        if m not in price:
            got = plan_choice(price, reactions, m, v, default)
            if got is None:
                return None
            pre += got[0]
    lines = pre + [line(reactions[r]) for r in out]
    try:
        c, st = run_case(price, [parse_reaction(l) for l in lines])
    except KeyError:
        return None
    if st.get(name, 0) < qty:
        return None
    return lines, c


def optimize(price, reactions, name, qty, tl=60, orders=30, seed_rng=1, rounds=10, log=False, agg_mode=False):
    unit = unit_costs(price, reactions)
    default = hill_default(price, reactions)
    cuts, best, obj0 = [], None, None
    rng = random.Random(seed_rng)
    for it in range(rounds):
        got = ilp(price, reactions, name, qty, unit, tl, cuts)
        if got is None:
            break
        count, seed, obj = got
        obj0 = obj if obj0 is None else obj0
        round_best, round_rep = None, None
        for k in range(orders):
            order = list(range(len(reactions)))
            if k:
                rng.shuffle(order)
            out, sd = fire(price, reactions, name, qty, count, seed, unit, order)
            b = build(price, reactions, name, qty, out, sd, default)
            if b and (round_best is None or b[1] < round_best[1]):
                round_best, round_rep = b, list(fire.repairs)
        if log:
            print('  round', it, 'ilp', round(obj), 'real', round_best[1] if round_best else None, flush=True)
        if round_best and (best is None or round_best[1] < best[1]):
            best = round_best
        if not round_rep:
            break
        if agg_mode:
            agg = {}
            for m, v, r in round_rep:
                agg[(m, r)] = agg.get((m, r), 0) + v
            have = {(m, r): v for m, v, r in cuts}
            if all(have.get(k, 0) >= v for k, v in agg.items()):
                break
            cuts = [(m, v, r) for m, v, r in cuts if (m, r) not in agg] + [(m, max(v, have.get((m, r), 0)), r) for (m, r), v in agg.items()]
        else:
            new = [(m, v, r) for m, v, r in round_rep if (m, v, r) not in cuts]
            if not new:
                break
            cuts += new
    return best, obj0


if __name__ == '__main__':
    f, i, outdir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    price, rx, tg = parse(open(f'C:/_repos/CCC26/Chemistry-Lab/level3/in_level-3_{f}.txt').read())
    n, q = tg[i]
    cands = []
    for mode, pen in ((False, True), (True, True), (False, False), (True, False)):
        FUTURE_PEN = pen
        for sr in (1, 2):
            b, _ = optimize(price, rx, n, q, tl=60, orders=60, seed_rng=sr, rounds=12, agg_mode=mode)
            if b:
                cands.append((b[1], 'ilp' + str(mode) + str(pen) + str(sr), b[0]))
    lines, c = hill_climb(price, rx, n, q, 60)
    cands.append((run_case(price, [parse_reaction(l) for l in lines])[0], 'hc', lines))
    cands.sort(key=lambda t: t[0])
    print(i, n, q, [(c, k) for c, k, _ in cands], flush=True)
    open(f'{outdir}/t{i}.txt', 'w').write(str(cands[0][0]) + '\n' + '\n'.join(cands[0][2]) + '\n')
