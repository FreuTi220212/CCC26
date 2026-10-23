import random
import sys

from level2 import parse_list, parse_reaction, run_case


TRIES = 40
SECONDS = 6.0
INIT = {}


def parse(data):
    """M Preise, Leerzeile, R Reaktionen, Leerzeile, N Zielmolekuele 'count name' -> (preise, [(edukte, produkte)], [(name, count)])."""
    lines = [l.strip() for l in data.splitlines()]
    m = int(lines[0])
    price = {}
    for l in lines[1:1 + m]:
        c, name = l.split("->")
        price[name.strip()] = int(c)
    i = 1 + m
    while not lines[i]:
        i += 1
    r = int(lines[i])
    reactions = [parse_reaction(l) for l in lines[i + 1:i + 1 + r]]
    i += 1 + r
    while not lines[i]:
        i += 1
    n = int(lines[i])
    targets = [parse_list(l)[0] for l in lines[i + 1:i + 1 + n]]
    return price, reactions, targets


def unit_costs(price, reactions):
    """Kosten je Molekuel = min(Kaufpreis, Edukt-Kosten der Reaktion / erzeugte Menge); Fixpunkt-Iteration (Nebenprodukte ohne Gutschrift)."""
    cost = dict(price)
    changed = True
    while changed:
        changed = False
        for idx, (edukte, produkte) in enumerate(reactions):
            if any(name not in cost for name, _ in edukte):
                continue
            total = sum(cost[name] * c for name, c in edukte)
            for name, c in produkte:
                if total / c < cost.get(name, float("inf")) - 1e-9:
                    cost[name] = total / c
                    changed = True
    return cost


# ---- Level 3: Reaktionsfolge, die das Ziel erzeugt (fehlende Grundmolekuele werden automatisch gekauft, Reste erlaubt).
# Je Molekuel die guenstigste Reaktion (Kosten je Einheit), rekursiv; Nebenprodukte bleiben im Bestand und werden wiederverwendet.
def plan(price, reactions, targets):
    cost = unit_costs(price, reactions)
    best = {}
    for idx, (edukte, produkte) in enumerate(reactions):
        if any(name not in cost for name, _ in edukte):
            continue
        total = sum(cost[name] * c for name, c in edukte)
        for name, c in produkte:
            if name not in price or total / c < cost[name] + 1e-9 or True:
                key = total / c
                if name not in best or key < best[name][0] - 1e-9:
                    best[name] = (key, idx)
    stock, out = {}, []

    def need(name, qty, depth=0):
        if depth > 60:
            raise RuntimeError("Zyklus bei " + name)
        have = stock.get(name, 0)
        if have >= qty:
            return
        if name in price and (name not in best or price[name] <= best[name][0] + 1e-9):
            stock[name] = qty  # kaufen (implizit)
            return
        edukte, produkte = reactions[best[name][1]]
        per = dict(produkte)[name]
        k = -(-(qty - have) // per)
        for _ in range(k):
            for e, c in edukte:
                need(e, c, depth + 1)
            for e, c in edukte:
                stock[e] -= c
            for p, c in produkte:
                stock[p] = stock.get(p, 0) + c
            out.append(f"{', '.join(f'{c} {e}' for e, c in edukte)} -> {', '.join(f'{c} {p}' for p, c in produkte)}")

    for name, qty in targets:
        need(name, qty)
        stock[name] -= qty  # Ziel gehoert nicht mehr zum frei verwendbaren Bestand (je Fall ein eigener Absatz)
        stock[name] += qty
    return out


def plan_choice(price, reactions, name, qty, choice):
    """Wie plan(), aber mit fester Wahl je Molekuel (Reaktionsindex oder None = kaufen). Rueckgabe (Zeilen, Kosten, benutzte Molekuele)."""
    stock, out, used, cost = {}, [], set(), [0]

    def need(m, q, depth=0):
        if depth > 40:
            raise RecursionError
        used.add(m)
        have = stock.get(m, 0)
        if have >= q:
            return
        r = choice.get(m)
        if r is None:
            cost[0] += price[m] * (q - have)
            stock[m] = q
            return
        edukte, produkte = reactions[r]
        per = dict(produkte)[m]
        for _ in range(-(-(q - have) // per)):
            for _round in range(len(edukte) + 1):  # Beschaffung eines Edukts kann den Bestand eines anderen verbrauchen
                for e, c in edukte:
                    need(e, c, depth + 1)
                if all(stock.get(e, 0) >= c for e, c in edukte):
                    break
            else:
                raise RecursionError
            for e, c in edukte:
                stock[e] -= c
            for p, c in produkte:
                stock[p] = stock.get(p, 0) + c
            out.append(f"{', '.join(f'{c} {e}' for e, c in edukte)} -> {', '.join(f'{c} {p}' for p, c in produkte)}")

    try:
        need(name, qty)
    except RecursionError:
        return None
    return out, cost[0], used


def hill_climb(price, reactions, name, qty, seconds=8.0):
    """Lokale Suche ueber die Wahl 'welche Reaktion erzeugt Molekuel m' (oder kaufen); Bewertung durch Simulation des ganzen Plans."""
    import time
    cost = unit_costs(price, reactions)
    prod = {}
    for idx, (edukte, produkte) in enumerate(reactions):
        if all(m in cost for m, _ in edukte):
            for m, c in produkte:
                prod.setdefault(m, []).append(idx)
    choice = {}
    for m in set(prod) | set(price):
        opts = [(sum(cost[e] * c for e, c in reactions[r][0]) / dict(reactions[r][1])[m], r) for r in prod.get(m, [])]
        best = min(opts)[1] if opts else None
        choice[m] = None if (m in price and (not opts or price[m] <= min(opts)[0] + 1e-9)) else best
    default = dict(choice)
    for m, r in INIT.items():  # Startwahl aus der ILP-Bilanzloesung (falls vorhanden)
        if m in choice and r in prod.get(m, []):
            choice[m] = r

    def evaluate(ch):
        got = plan_choice(price, reactions, name, qty, ch)
        if got is None:
            return None
        try:
            return got[0], run_case(price, [parse_reaction(l) for l in got[0]])[0], got[2]
        except KeyError:
            return None

    def climb(ch, cur):
        improved = True
        while improved and time.time() - t0 < seconds:
            improved = False
            for m in sorted(cur[2]):
                for alt in list(prod.get(m, [])) + ([None] if m in price else []):
                    if alt == ch.get(m):
                        continue
                    old, ch[m] = ch.get(m), alt
                    got = evaluate(ch)
                    if got and got[1] < cur[1]:
                        cur, improved = got, True
                    else:
                        ch[m] = old
        return cur

    t0 = time.time()
    rng = random.Random(7)
    if evaluate(choice) is None:  # Startwahl nicht ausfuehrbar (Zyklus): Standardwahl
        choice.clear()
        choice.update(default)
    best_ch, best = dict(choice), climb(choice, evaluate(choice))
    while time.time() - t0 < seconds:  # Neustarts: einige Entscheidungen zufaellig aendern, wieder bergauf
        ch = dict(best_ch)
        for m in rng.sample(sorted(best[2]), min(len(best[2]), rng.randint(2, 6))):
            alts = list(prod.get(m, [])) + ([None] if m in price else [])
            ch[m] = rng.choice(alts)
        cur = evaluate(ch)
        if cur is None:
            continue
        cur = climb(ch, cur)
        if cur[1] < best[1]:
            best_ch, best = dict(ch), cur
    return best[0], best[1]


def plan_ilp(price, reactions, name, qty):
    """Exakt kostenminimal: x_r = Anzahl Ausfuehrungen, b_m = Zukaeufe; Bilanz je Molekuel >= Ziel; danach topologisch einsortieren."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    mols = sorted({m for e, p in reactions for m, _ in e + p} | set(price) | {name})
    mi = {m: i for i, m in enumerate(mols)}
    R, B = len(reactions), [m for m in mols if m in price]
    bi = {m: R + i for i, m in enumerate(B)}
    NB = [m for m in mols if m not in price]
    ni = {m: i for i, m in enumerate(NB)}
    nx = R + len(B)  # Variablen: x (R), b (|B|), y (R, Reaktion benutzt), lvl (|NB|, Stufe der nicht kaufbaren Molekuele)
    ny, nl = nx + R, nx + R + len(NB)
    A = np.zeros((len(mols), nl))
    for r, (e, p) in enumerate(reactions):
        for m, c in e:
            A[mi[m], r] -= c
        for m, c in p:
            A[mi[m], r] += c
    for m in B:
        A[mi[m], bi[m]] = 1
    lo = np.zeros(len(mols))
    lo[mi[name]] = qty
    big = qty * 60 + 60
    rows, rlo, rhi = [], [], []
    for r, (e, p) in enumerate(reactions):
        row = np.zeros(nl)  # x_r <= big * y_r
        row[r], row[nx + r] = -1, big
        rows.append(row), rlo.append(0), rhi.append(np.inf)
        for me, _ in e:
            for mp, _ in p:
                if me in ni and mp in ni and me != mp:  # benutzt: lvl[p] >= lvl[e] + 1 (verbietet Zyklen ohne Startbestand)
                    row = np.zeros(nl)
                    row[ny + ni[mp]], row[ny + ni[me]], row[nx + r] = 1, -1, -len(NB)
                    rows.append(row), rlo.append(1 - len(NB)), rhi.append(np.inf)
    c = np.array([0.0] * R + [float(price[m]) for m in B] + [0.0] * (R + len(NB)))
    integ = np.concatenate([np.ones(nx + R), np.zeros(len(NB))])
    ub = np.concatenate([np.full(nx, np.inf), np.ones(R), np.full(len(NB), float(len(NB)))])
    res = milp(c, constraints=[LinearConstraint(A, lo, np.inf), LinearConstraint(np.array(rows), rlo, rhi)],
               integrality=integ, bounds=Bounds(np.zeros(nl), ub), options={"time_limit": 12})
    if res.x is None:
        return None
    plan_ilp.last = res.fun
    count = [int(round(v)) for v in res.x[:R]]
    # Reihenfolge: Reaktion ausfuehren, sobald alle NICHT kaufbaren Edukte im Bestand sind (Kaufbares wird bei Bedarf gekauft).
    best = None
    rng = random.Random(1)
    for attempt in range(TRIES):
        order = list(range(R))
        if attempt:
            rng.shuffle(order)
        got = schedule(price, reactions, name, qty, count, {m: int(round(res.x[bi[m]])) for m in B}, order)
        if got and (best is None or got[1] < best[1]):
            best = got
    return best[0] if best else None


def schedule(price, reactions, name, qty, count, budget, order):
    """Reihenfolge der Reaktionen (Menge steht fest) mit moeglichst wenigen Zukaeufen: erst ohne Zukauf, dann Zukauf nur fuer nicht mehr
    erzeugte Molekuele, dann im Budgetrahmen, zuletzt billigster Anschub. Rueckgabe (Zeilen, Kosten) oder None."""
    R = len(reactions)

    def deficit(r):
        return {m: c - stock.get(m, 0) for m, c in reactions[r][0] if c > stock.get(m, 0)}

    stock, out, left, cost = {}, [], list(count), 0
    while any(left):
        pick = None
        pending = {m for r in range(R) if left[r] for m, _ in reactions[r][1]}  # Molekuele, die noch erzeugt werden
        for allow_buy in (0, 1, 2):
            for r in order:
                if not left[r]:
                    continue
                d = deficit(r)
                if not d or (allow_buy and all(m in budget and budget[m] >= v and (allow_buy == 2 or m not in pending)
                                               for m, v in d.items())):
                    pick = (r, d)
                    break
            if pick:
                break
        if pick is None:  # Zyklus ohne Startbestand: billigsten Anschub zukaufen
            options = []
            for r in range(R):
                d = deficit(r) if left[r] else None
                if d and all(m in price for m in d):
                    options.append((sum(price[m] * v for m, v in d.items()), r, d))
            if not options:
                return None
            _, r, d = min(options)
            pick = (r, d)
        r, d = pick
        for m, v in d.items():
            if m in budget:
                budget[m] -= v
            cost += price[m] * v
            stock[m] = stock.get(m, 0) + v
        e, p = reactions[r]
        for m, c in e:
            stock[m] -= c
        for m, c in p:
            stock[m] = stock.get(m, 0) + c
        out.append(f"{', '.join(f'{c} {m}' for m, c in e)} -> {', '.join(f'{c} {m}' for m, c in p)}")
        left[r] -= 1
    return (out, cost) if stock.get(name, 0) >= qty else None


def plan_siphon(price, reactions, name, qty, seconds=60.0, milp_seconds=20.0):
    """Exakte Kostenminimierung per ILP (Bilanz) + Lazy-Cuts gegen 'Katalysator/Zyklus ohne Startbestand' (Siphon-Schnitte, wie bei
    Petri-Netzen): ILP loesen, Reaktionen feuern lassen; bleibt es haengen, den leeren Siphon suchen und einen Schnitt hinzufuegen:
    benutzt eine Reaktion r einen Molekuel-Satz S, dann muss S Startbestand (Kauf) haben oder von aussen erzeugt werden."""
    import time
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    t0 = time.time()
    mols = sorted({m for e, p in reactions for m, _ in e + p} | set(price) | {name})
    mi = {m: i for i, m in enumerate(mols)}
    R = len(reactions)
    B = [m for m in mols if m in price]
    bi = {m: R + i for i, m in enumerate(B)}
    nx = R + len(B)
    nl = nx + R  # x (R), b (|B|), y (R)
    A = np.zeros((len(mols), nl))
    for r, (e, p) in enumerate(reactions):
        for m, c in e:
            A[mi[m], r] -= c
        for m, c in p:
            A[mi[m], r] += c
    for m in B:
        A[mi[m], bi[m]] = 1
    lo = np.zeros(len(mols))
    lo[mi[name]] = qty
    big = qty * 60 + 60
    rows, rlo = [], []
    for r in range(R):
        row = np.zeros(nl)
        row[r], row[nx + r] = -1, big
        rows.append(row)
        rlo.append(0)
    consumes = [{m for m, _ in e} for e, _ in reactions]
    produces = [{m for m, _ in p} for _, p in reactions]
    c = np.array([0.0] * R + [float(price[m]) for m in B] + [0.0] * R)
    integ, ub = np.ones(nl), np.concatenate([np.full(nx, np.inf), np.ones(R)])
    best = None
    seen = set()
    while time.time() - t0 < seconds:
        cons = [LinearConstraint(A, lo, np.inf)]
        if rows:
            cons.append(LinearConstraint(np.array(rows), np.array(rlo), np.inf))
        res = milp(c, constraints=cons, integrality=integ, bounds=Bounds(np.zeros(nl), ub), options={"time_limit": milp_seconds})
        if res.x is None:
            return best
        count = [int(round(v)) for v in res.x[:R]]
        stock = {m: int(round(res.x[bi[m]])) for m in B}
        left, out = count[:], []
        progress = True
        while progress:  # alles feuern, was mit dem Bestand geht
            progress = False
            for r in range(R):
                while left[r] and all(stock.get(m, 0) >= q for m, q in reactions[r][0]):
                    for m, q in reactions[r][0]:
                        stock[m] -= q
                    for m, q in reactions[r][1]:
                        stock[m] = stock.get(m, 0) + q
                    left[r] -= 1
                    out.append(f"{', '.join(f'{q} {m}' for m, q in reactions[r][0])} -> {', '.join(f'{q} {m}' for m, q in reactions[r][1])}")
                    progress = True
        if not any(left):
            return out
        # Haengen geblieben: groessten leeren Siphon bzgl. der uebrigen Reaktionen suchen
        rest = [r for r in range(R) if left[r]]
        sip = {m for r in rest for m in consumes[r] | produces[r] if stock.get(m, 0) == 0}
        changed = True
        while changed:
            changed = False
            for m in list(sip):
                if any(m in produces[r] and not (consumes[r] & sip) for r in rest):
                    sip.discard(m)
                    changed = True
        stuck = [r for r in rest if consumes[r] & sip]
        if not sip or not stuck:
            return best  # Haengen durch Konkurrenz um Bestand, kein Siphon: aufgeben
        key = frozenset(sip)
        ext = [r for r in range(R) if produces[r] & sip and not (consumes[r] & sip)]
        added = False
        for r in stuck:
            if (key, r) in seen:
                continue
            seen.add((key, r))
            row = np.zeros(nl)
            for m in sip & set(B):
                row[bi[m]] += 1
            for q in ext:
                row[nx + q] += 1
            row[nx + r] -= 1
            rows.append(row)
            rlo.append(0)
            added = True
        if not added:
            return best
    return best


def plan_exact(price, reactions, name, qty, seconds=40.0, milp_seconds=15.0):
    """ILP ueber Reaktionsanzahlen x_r und Startbestand s_m. Jedes Molekuel darf als Startbestand 'gekauft' werden: kaufbare zum Preis,
    andere zu ihren Herstellkosten (Seed wird vorab per Greedy-Kette erzeugt). Katalysatoren/Zyklen brauchen Startbestand (direkte
    Nebenbedingung + Lazy-Siphon-Schnitte). Die Reaktionen werden dann feuerfaehig sortiert; Kosten durch Simulation geprueft."""
    import time
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    t0 = time.time()
    unit = unit_costs(price, reactions)
    mols = sorted({m for e, p in reactions for m, _ in e + p} | set(price) | {name})
    mi = {m: i for i, m in enumerate(mols)}
    R, M = len(reactions), len(mols)
    nx, nl = R, R + M + R  # x (R), s (M), y (R)
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
    big = qty * 60 + 60
    rows, rlo = [], []
    consumes = [{m for m, _ in e} for e, _ in reactions]
    produces = [{m for m, _ in p} for _, p in reactions]
    for r in range(R):
        row = np.zeros(nl)
        row[r], row[R + M + r] = -1, big
        rows.append(row), rlo.append(0)
        row = np.zeros(nl)  # y_r <= x_r (benutzt heisst wirklich ausgefuehrt)
        row[r], row[R + M + r] = 1, -1
        rows.append(row), rlo.append(0)
        for m in consumes[r] & produces[r]:  # Katalysator: braucht Bestand von aussen (Start oder andere Erzeuger)
            row = np.zeros(nl)
            row[R + mi[m]] = 1
            for q in range(R):
                if q != r and m in produces[q] and m not in consumes[q]:
                    row[q] = 1
            row[R + M + r] = -1
            rows.append(row), rlo.append(0)
    cost_s = np.array([float(price[m]) if m in price else float(unit.get(m, 1e6)) for m in mols])
    c = np.concatenate([np.zeros(R), cost_s, np.zeros(R)])
    integ = np.ones(nl)
    ub = np.concatenate([np.full(R + M, np.inf), np.ones(R)])
    best = None
    seen = set()
    while time.time() - t0 < seconds:
        res = milp(c, constraints=[LinearConstraint(A, lo, np.inf), LinearConstraint(np.array(rows), np.array(rlo), np.inf)],
                   integrality=integ, bounds=Bounds(np.zeros(nl), ub), options={"time_limit": milp_seconds})
        if res.x is None:
            return best
        count = [int(round(v)) for v in res.x[:R]]
        seed = {m: int(round(res.x[R + mi[m]])) for m in mols if round(res.x[R + mi[m]]) > 0}
        rep = 0
        stock, left, out = dict(seed), count[:], []
        while True:
            progress = True
            while progress:
                progress = False
                for r in range(R):
                    while left[r] and all(stock.get(m, 0) >= q for m, q in reactions[r][0]):
                        for m, q in reactions[r][0]:
                            stock[m] -= q
                        for m, q in reactions[r][1]:
                            stock[m] = stock.get(m, 0) + q
                        left[r] -= 1
                        out.append(f"{', '.join(f'{q} {m}' for m, q in reactions[r][0])} -> {', '.join(f'{q} {m}' for m, q in reactions[r][1])}")
                        progress = True
            rest = [r for r in range(R) if left[r]]
            if not rest or rep > 60:
                break
            # Haengen ohne leeren Siphon (zu wenig Bestand): fehlende Menge der billigsten Reaktion als Startbestand ergaenzen
            sip0 = {m for r in rest for m in consumes[r] | produces[r] if stock.get(m, 0) == 0}
            closed = set(sip0)
            ch = True
            while ch:
                ch = False
                for m in list(closed):
                    if any(m in produces[r] and not (consumes[r] & closed) for r in rest):
                        closed.discard(m)
                        ch = True
            if closed:
                break  # echter leerer Siphon: unten Schnitt erzeugen
            options = []
            for r in rest:
                d = {m: q - stock.get(m, 0) for m, q in reactions[r][0] if q > stock.get(m, 0)}
                options.append((sum((price[m] if m in price else unit.get(m, 1e6)) * v for m, v in d.items()), r, d))
            _, r, d = min(options)
            for m, v in d.items():
                stock[m] = stock.get(m, 0) + v
                seed[m] = seed.get(m, 0) + v
            rep += 1
        if not any(left) and stock.get(name, 0) >= qty:
            pre = []  # Seeds nicht kaufbarer Molekuele vorab herstellen
            for m, v in seed.items():
                if m not in price:
                    got = plan_choice(price, reactions, m, v, hill_default(price, reactions))
                    if got is None:
                        return best
                    pre += got[0]
            plan_lines = pre + out
            try:
                real = run_case(price, [parse_reaction(l) for l in plan_lines])
            except KeyError:
                return best
            if real[1].get(name, 0) >= qty and (best is None or real[0] < best[1]):
                best = (plan_lines, real[0])
            return best
        rest = [r for r in range(R) if left[r]]
        sip = {m for r in rest for m in consumes[r] | produces[r] if stock.get(m, 0) == 0}
        changed = True
        while changed:
            changed = False
            for m in list(sip):
                if any(m in produces[r] and not (consumes[r] & sip) for r in rest):
                    sip.discard(m)
                    changed = True
        stuck = [r for r in rest if consumes[r] & sip]
        if not sip or not stuck:
            return best
        added = False
        for r in stuck[:12]:
            for m0 in sorted(consumes[r] & sip)[:2]:
                small = {m0}  # kleiner Siphon: rueckwaerts abschliessen, je Erzeuger ein leeres Edukt aufnehmen
                todo = [m0]
                while todo:
                    p_ = todo.pop()
                    for q in rest:
                        if p_ in produces[q] and not (consumes[q] & small):
                            cand = sorted(consumes[q] & sip)
                            if cand:
                                small.add(cand[0])
                                todo.append(cand[0])
                key = (frozenset(small), r)
                if key in seen:
                    continue
                seen.add(key)
                ext = [q for q in range(R) if produces[q] & small and not (consumes[q] & small)]
                row = np.zeros(nl)
                for m in small:
                    row[R + mi[m]] += 1
                for q in ext:
                    row[R + M + q] += 1
                row[R + M + r] -= 1
                rows.append(row), rlo.append(0)
                added = True
        if not added:
            return best
    return best


def hill_default(price, reactions):
    """Standardwahl je Molekuel (guenstigste Reaktion nach Einheitskosten) fuer plan_choice."""
    cost = unit_costs(price, reactions)
    choice = {}
    for m in set(cost):
        opts = []
        for r, (e, p) in enumerate(reactions):
            if all(x in cost for x, _ in e) and any(m == q for q, _ in p):
                opts.append((sum(cost[x] * c for x, c in e) / dict(p)[m], r))
        if opts:
            choice[m] = None if (m in price and price[m] <= min(opts)[0] + 1e-9) else min(opts)[1]
        elif m in price:
            choice[m] = None
    return choice


def solve(data):
    price, reactions, targets = parse(data)
    paragraphs = []
    for name, qty in targets:
        rs, cost = hill_climb(price, reactions, name, qty, SECONDS)
        alt = plan_ilp(price, reactions, name, qty)  # zweiter Weg (ILP + Einsortieren); den billigeren, tatsaechlich simulierten Plan nehmen
        if alt is not None and run_case(price, [parse_reaction(l) for l in alt])[0] < cost:
            rs = alt
        paragraphs.append("\n".join(rs))
    return "\n\n".join(paragraphs) + "\n\n"  # Beispiel-Output endet mit Leerzeile


def validate(inp, out):
    price, reactions, targets = parse(inp)
    paragraphs = out.rstrip("\n").split("\n\n")
    if len(paragraphs) != len(targets):
        return f"{len(paragraphs)} Absaetze statt {len(targets)}"
    known = {(tuple(e), tuple(p)) for e, p in reactions}
    for para, (name, qty) in zip(paragraphs, targets):
        rs = [parse_reaction(l) for l in para.split("\n") if l.strip()]
        if any((tuple(e), tuple(p)) not in known for e, p in rs):
            return f"{name}: unbekannte Reaktion"
        _, stock = run_case(price, rs)
        if stock.get(name, 0) < qty:
            return f"{name}: nur {stock.get(name, 0)} von {qty}"
    return None


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
