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


# ---- Level 3: je Waehrung alle Betraege 1..100 mit moeglichst wenigen Muenzen (Input wie Level 1)
MAX_AMOUNT = 100


def min_coin_table(coins, limit=MAX_AMOUNT):
    """best[a] = (Anzahl, letzte Muenze) fuer kleinste Muenzanzahl, Betrag a (unbegrenzt viele Muenzen)."""
    inf = float("inf")
    best = [(0, 0)] + [(inf, 0)] * limit
    for a in range(1, limit + 1):
        for c in coins:
            if c <= a and best[a - c][0] + 1 < best[a][0]:
                best[a] = (best[a - c][0] + 1, c)
    return best


def change(best, amount):
    cnt = {}
    while amount:
        c = best[amount][1]
        cnt[c] = cnt.get(c, 0) + 1
        amount -= c
    return " ".join(f"{n}x{c}" for c, n in sorted(cnt.items(), reverse=True))


def validate(inp, out):
    """None wenn ok, sonst Fehlertext."""
    cur = parse(inp)
    lines = out.strip().splitlines()
    if len(lines) != len(cur) * MAX_AMOUNT:
        return f"{len(lines)} Zeilen statt {len(cur) * MAX_AMOUNT}"
    i = 0
    for coins in cur:
        best = min_coin_table(coins)
        have = set(coins)
        for amount in range(1, MAX_AMOUNT + 1):
            total = n_coins = 0
            for tok in lines[i].split():
                k, c = tok.split("x")
                k, c = int(k), int(c)
                if c not in have or k <= 0:
                    return f"Zeile {i + 1}: ungueltige Muenze {tok}"
                total += k * c
                n_coins += k
            i += 1
            if total != amount or n_coins != best[amount][0]:
                return f"Zeile {i}: Summe {total} (Betrag {amount}), {n_coins} Muenzen statt {best[amount][0]}"
    return None


def solve(data):
    out = []
    for coins in parse(data):
        best = min_coin_table(coins)
        out += [change(best, a) for a in range(1, MAX_AMOUNT + 1)]
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
