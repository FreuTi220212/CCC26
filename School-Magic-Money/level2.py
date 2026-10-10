import sys


def parse(data):
    t = data.split()
    n, c = int(t[0]), int(t[1])
    return [[int(x) for x in t[2 + i * c:2 + (i + 1) * c]] for i in range(n)]


def smallest_not_single_coin(coins):
    have = set(coins)
    x = 1
    while x in have:
        x += 1
    return x


# ---- Level 2: je Betrag zwei Muenzen (auch gleiche) mit Summe = Betrag. Mehrere Loesungen moeglich.
def parse2(data):
    t = data.split()
    n, c, a = int(t[0]), int(t[1]), int(t[2])
    pos, res = 3, []
    for _ in range(n):
        coins = [int(x) for x in t[pos:pos + c]]
        amounts = [int(x) for x in t[pos + c:pos + c + a]]
        pos += c + a
        res.append((coins, amounts))
    return res


def two_coins(have, amount):
    for x in sorted(have):
        if 2 * x > amount:
            break
        if amount - x in have:
            return x, amount - x
    raise ValueError(f"keine Loesung fuer {amount}")


def validate(inp, out):
    """None wenn ok, sonst Fehlertext."""
    cur = parse2(inp)
    lines = out.strip().splitlines()
    total = sum(len(a) for _, a in cur)
    if len(lines) != total:
        return f"{len(lines)} Zeilen statt {total}"
    i = 0
    for coins, amounts in cur:
        have = set(coins)
        for amount in amounts:
            parts = lines[i].split()
            i += 1
            if len(parts) != 2:
                return f"Zeile {i}: kein Paar"
            x, y = int(parts[0]), int(parts[1])
            if x not in have or y not in have or x + y != amount:
                return f"Zeile {i}: {x}+{y} != {amount} oder keine Muenzen"
    return None


def solve(data):
    out = []
    for coins, amounts in parse2(data):
        have = set(coins)
        for amount in amounts:
            x, y = two_coins(have, amount)
            out.append(f"{x} {y}")
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
