import sys


def parse(data):
    t = data.split()
    n, c = int(t[0]), int(t[1])
    return [[int(x) for x in t[2 + i * c:2 + (i + 1) * c]] for i in range(n)]


def parse2(data):
    """Level 2+: N, C, A, dann je Waehrung Muenzzeile + Betragszeile."""
    t = data.split()
    n, c, a = int(t[0]), int(t[1]), int(t[2])
    pos, res = 3, []
    for _ in range(n):
        coins = [int(x) for x in t[pos:pos + c]]
        amounts = [int(x) for x in t[pos + c:pos + c + a]]
        pos += c + a
        res.append((coins, amounts))
    return res


def min_coin_table(coins, limit):
    """best[a] = (Anzahl, letzte Muenze) fuer kleinste Muenzanzahl, Betrag a (unbegrenzt viele Muenzen)."""
    inf = float("inf")
    best = [(0, 0)] + [(inf, 0)] * limit
    for a in range(1, limit + 1):
        for c in coins:
            if c <= a and best[a - c][0] + 1 < best[a][0]:
                best[a] = (best[a - c][0] + 1, c)
    return best


def format_counts(cnt):
    return " ".join(f"{n}x{c}" for c, n in sorted(cnt.items(), reverse=True) if n)


# ---- Level 3: kleine Betraege (1..100), Tabelle direkt
def change(best, amount):
    cnt = {}
    while amount:
        c = best[amount][1]
        cnt[c] = cnt.get(c, 0) + 1
        amount -= c
    return format_counts(cnt)


# ---- Level 4: Betraege bis ~1e9. Optimal: mind. so viele Kopien der groessten Muenze M, dass der Rest in die
# Tabelle (bis LIM = 2*M*M) passt, denn die uebrigen Muenzen summieren sich auf hoechstens (M-1)^2.
def make_solver(coins, factor=2):
    big = max(coins)
    limit = factor * big * big
    best = min_coin_table(coins, limit)

    def count_and_change(amount):
        cnt = {}
        if amount > limit:
            k = (amount - limit) // big + 1
            cnt[big] = k
            amount -= k * big
        while amount:
            c = best[amount][1]
            cnt[c] = cnt.get(c, 0) + 1
            amount -= c
        return cnt

    return count_and_change


def validate(inp, out):
    """None wenn ok, sonst Fehlertext."""
    cur = parse2(inp)
    lines = out.strip().splitlines()
    total_lines = sum(len(a) for _, a in cur)
    if len(lines) != total_lines:
        return f"{len(lines)} Zeilen statt {total_lines}"
    i = 0
    for coins, amounts in cur:
        have = set(coins)
        check = make_solver(coins, factor=4)  # unabhaengige Gegenprobe mit anderer Tabellengroesse
        for amount in amounts:
            total = n_coins = 0
            for tok in lines[i].split():
                k, c = tok.split("x")
                k, c = int(k), int(c)
                if c not in have or k <= 0:
                    return f"Zeile {i + 1}: ungueltige Muenze {tok}"
                total += k * c
                n_coins += k
            i += 1
            opt = sum(check(amount).values())
            if total != amount or n_coins != opt:
                return f"Zeile {i}: Summe {total} (Betrag {amount}), {n_coins} Muenzen statt {opt}"
    return None


def solve(data):
    out = []
    for coins, amounts in parse2(data):
        solver = make_solver(coins)
        out += [format_counts(solver(a)) for a in amounts]
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
