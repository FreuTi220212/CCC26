import sys


def parse_list(text):
    """'3 H2, 4 O2' -> [(name, count), ...] in Reihenfolge (leer -> [])."""
    return [(name, int(c)) for c, name in (item.split() for item in text.split(",") if item.strip())]


def parse_reaction(line):
    left, right = line.split("->")
    return parse_list(left), parse_list(right)


def parse(data):
    """M Preise 'cost -> molecule', Leerzeile, N Faelle: R, R Reaktionen, Leerzeile -> (preise, [[reaktionen]])."""
    lines = [l.strip() for l in data.splitlines()]
    m = int(lines[0])
    price = {}
    for l in lines[1:1 + m]:
        c, name = l.split("->")
        price[name.strip()] = int(c)
    i = 1 + m
    while not lines[i]:
        i += 1
    n, i, cases = int(lines[i]), i + 1, []
    for _ in range(n):
        while not lines[i]:
            i += 1
        r = int(lines[i])
        cases.append([parse_reaction(l) for l in lines[i + 1:i + 1 + r]])
        i += 1 + r
    return price, cases


# ---- Level 2: Inventar startet leer; fehlende Edukte werden zum Einzelpreis nachgekauft, dann reagiert. Ausgabe 'Kosten -> Inventar'
# in Einfuege-Reihenfolge der Molekuele (Eintraege mit Menge 0 bleiben an ihrer Stelle, werden nur nicht ausgegeben).
def run_case(price, reactions):
    stock, cost = {}, 0
    for edukte, produkte in reactions:
        need = {}
        for name, c in edukte:
            need[name] = need.get(name, 0) + c
        for name, c in need.items():
            missing = c - stock.get(name, 0)
            if missing > 0:
                cost += missing * price[name]
                stock[name] = stock.get(name, 0) + missing
            else:
                stock.setdefault(name, 0)
        for name, c in need.items():
            stock[name] -= c
        for name, c in produkte:
            stock[name] = stock.get(name, 0) + c
    return cost, stock


def solve(data):
    price, cases = parse(data)
    out = []
    for reactions in cases:
        cost, stock = run_case(price, reactions)
        out.append(f"{cost} -> " + ", ".join(f"{v} {k}" for k, v in stock.items() if v))
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
