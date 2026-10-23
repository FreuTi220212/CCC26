import sys


def parse_list(text):
    """'3 H2, 4 O2' -> [(name, count), ...] in Reihenfolge (leer -> [])."""
    return [(name, int(c)) for c, name in (item.split() for item in text.split(",") if item.strip())]


def parse(data):
    """N, dann je Fall: Inventar-Zeile, Reaktionszeile 'A -> B', Leerzeile -> [(inventar, (edukte, produkte))]."""
    lines = [l.strip() for l in data.splitlines()]
    n, cases, i = int(lines[0]), [], 1
    while len(cases) < n:
        while not lines[i]:
            i += 1
        left, right = lines[i + 1].split("->")
        cases.append((parse_list(lines[i]), (parse_list(left), parse_list(right))))
        i += 2
    return cases


def react_once(inventory, reaction):
    """Reaktion einmal ausfuehren: Edukte abziehen, Produkte addieren. Reihenfolge: Inventar, dann neue Produkte; Menge 0 entfaellt."""
    stock = {}
    for name, c in inventory:
        stock[name] = stock.get(name, 0) + c
    for name, c in reaction[0]:
        stock[name] = stock.get(name, 0) - c
    for name, c in reaction[1]:
        stock[name] = stock.get(name, 0) + c
    return {k: v for k, v in stock.items() if v != 0}


def fmt(stock):
    return ", ".join(f"{v} {k}" for k, v in stock.items())


def solve(data):
    return "\n".join(fmt(react_once(inv, rea)) for inv, rea in parse(data)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
