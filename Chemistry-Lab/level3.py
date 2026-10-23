import sys

from level2 import parse_list, parse_reaction, run_case


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


def plan_ilp(price, reactions, name, qty):
    """Exakt kostenminimal: x_r = Anzahl Ausfuehrungen, b_m = Zukaeufe; Bilanz je Molekuel >= Ziel; danach topologisch einsortieren."""
    import numpy as np
    from scipy.optimize import LinearConstraint, milp
    mols = sorted({m for e, p in reactions for m, _ in e + p} | set(price) | {name})
    mi = {m: i for i, m in enumerate(mols)}
    R, B = len(reactions), [m for m in mols if m in price]
    bi = {m: R + i for i, m in enumerate(B)}
    A = np.zeros((len(mols), R + len(B)))
    for r, (e, p) in enumerate(reactions):
        for m, c in e:
            A[mi[m], r] -= c
        for m, c in p:
            A[mi[m], r] += c
    for m in B:
        A[mi[m], bi[m]] = 1
    lo = np.zeros(len(mols))
    lo[mi[name]] = qty
    c = np.array([0.0] * R + [float(price[m]) for m in B])
    res = milp(c, constraints=LinearConstraint(A, lo, np.inf), integrality=np.ones(R + len(B)), bounds=(0, np.inf))
    if not res.success:
        return None
    count = [int(round(v)) for v in res.x[:R]]
    # Reihenfolge: Reaktion ausfuehren, sobald alle NICHT kaufbaren Edukte im Bestand sind (Kaufbares wird bei Bedarf gekauft).
    budget = {m: int(round(res.x[bi[m]])) for m in B}  # geplante Zukaeufe je kaufbarem Molekuel

    def deficit(r):
        return {m: c - stock.get(m, 0) for m, c in reactions[r][0] if c > stock.get(m, 0)}

    stock, out, left = {}, [], count[:]
    while any(left):
        pick = None
        for allow_buy in (False, True):  # erst Reaktionen ohne Zukauf, dann mit Zukauf im Rahmen des geplanten Budgets
            for r in range(R):
                if not left[r]:
                    continue
                d = deficit(r)
                if not d or (allow_buy and all(m in budget and budget[m] >= v for m, v in d.items())):
                    pick = (r, d)
                    break
            if pick:
                break
        if pick is None:  # uebrig sind nur nicht ausfuehrbare Leerlauf-Zyklen (Kosten 0): weglassen, sofern das Ziel erreicht ist
            break
        r, d = pick
        for m, v in d.items():
            budget[m] -= v
            stock[m] = stock.get(m, 0) + v
        e, p = reactions[r]
        for m, c in e:
            stock[m] -= c
        for m, c in p:
            stock[m] = stock.get(m, 0) + c
        out.append(f"{', '.join(f'{c} {m}' for m, c in e)} -> {', '.join(f'{c} {m}' for m, c in p)}")
        left[r] -= 1
    return out if stock.get(name, 0) >= qty else None


def solve(data):
    price, reactions, targets = parse(data)
    paragraphs = []
    for name, qty in targets:
        rs = plan_ilp(price, reactions, name, qty)
        if rs is None:
            rs = plan(price, reactions, [(name, qty)])
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
