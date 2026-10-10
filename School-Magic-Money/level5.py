import sys
from functools import lru_cache


def parse5(data):
    """Level 5: N, C, A; je Waehrung C Tokens 'nxv' (Vorrat) und A Betraege."""
    t = data.split()
    n, c, a = int(t[0]), int(t[1]), int(t[2])
    pos, res = 3, []
    for _ in range(n):
        inv = {}
        for tok in t[pos:pos + c]:
            k, v = tok.split("x")
            inv[int(v)] = int(k)
        amounts = [int(x) for x in t[pos + c:pos + c + a]]
        pos += c + a
        res.append((inv, amounts))
    return res


def format_counts(cnt):
    return " ".join(f"{n}x{c}" for c, n in sorted(cnt.items(), reverse=True) if n)


# ---- Level 5: begrenzter Vorrat je Muenzwert, min. Muenzen fuer Betraege bis ~1e9.
# Sei M der groesste Wert, n sein Vorrat. In einem optimalen Ergebnis gilt entweder x_M > n-(M-1)
# (Tausch "M Muenzen anderer Werte -> weniger M-Muenzen" nicht moeglich) oder es gibt hoechstens M-1 kleinere Muenzen.
#  - Fall 1: x_M in [n-M+2, n] ausprobieren, Rest mit den kleineren Werten loesen (Memo ueber (Ebene, Rest)).
#  - Fall 2: kleine Muenzen per DP-Tabelle (Summe <= (M-1)*v_vorletzter), Rest mit M-Muenzen auffuellen.
class Solver:
    def __init__(self, inv):
        self.vals = sorted(inv)
        self.inv = inv
        self.tables = {}
        self.memo = {}

    def small_table(self, k):
        """Tabelle fuer Wert-Indizes 0..k-1 mit Vorrat <= M-1 (M = vals[k]); (dp, choices)."""
        if k in self.tables:
            return self.tables[k]
        m = self.vals[k]
        top = max(self.vals[:k], default=0)
        limit = (m - 1) * top
        inf = float("inf")
        dp = [0] + [inf] * limit
        choices = []
        for j in range(k):
            v, cap = self.vals[j], min(self.inv[self.vals[j]], m - 1)
            new, ch = [inf] * (limit + 1), [0] * (limit + 1)
            for s in range(limit + 1):
                bt = inf
                for t in range(0, cap + 1):
                    if t * v > s:
                        break
                    if dp[s - t * v] + t < bt:
                        bt, ch[s] = dp[s - t * v] + t, t
                new[s] = bt
            dp = new
            choices.append(ch)
        self.tables[k] = (dp, choices, limit)
        return self.tables[k]

    def solve(self, k, amount):
        """(Anzahl, Plan) mit Muenzen 0..k; Plan = ('f1', x, Rest-Betrag) / ('f2', s) / None."""
        if k < 0:
            return (0, None) if amount == 0 else (float("inf"), None)
        key = (k, amount)
        if key in self.memo:
            return self.memo[key]
        m, n = self.vals[k], self.inv[self.vals[k]]
        best, plan = float("inf"), None
        # Fall 1
        for x in range(max(0, n - m + 2), n + 1):
            if x * m > amount:
                break
            sub, _ = self.solve(k - 1, amount - x * m)
            if x + sub < best:
                best, plan = x + sub, ("f1", x)
        # Fall 2
        dp, _, limit = self.small_table(k)
        for s in range(amount % m, min(limit, amount) + 1, m):
            if dp[s] == float("inf"):
                continue
            x = (amount - s) // m
            if x <= n and x + dp[s] < best:
                best, plan = x + dp[s], ("f2", s)
        self.memo[key] = (best, plan)
        return self.memo[key]

    def counts(self, amount):
        k = len(self.vals) - 1
        cnt = {}
        while k >= 0 and amount > 0:
            best, plan = self.solve(k, amount)
            if plan is None:
                raise ValueError(f"nicht moeglich: {amount}")
            m = self.vals[k]
            if plan[0] == "f1":
                x = plan[1]
                cnt[m] = x
                amount -= x * m
                k -= 1
            else:
                s = plan[1]
                x = (amount - s) // m
                cnt[m] = x
                _, choices, _ = self.small_table(k)
                for j in range(k - 1, -1, -1):
                    t = choices[j][s]
                    if t:
                        cnt[self.vals[j]] = t
                    s -= t * self.vals[j]
                amount = 0
        return cnt


def validate(inp, out):
    """None wenn ok, sonst Fehlertext (Summe und Vorrat; Optimalitaet siehe Entwicklungstest)."""
    cur = parse5(inp)
    lines = out.strip().splitlines()
    total_lines = sum(len(a) for _, a in cur)
    if len(lines) != total_lines:
        return f"{len(lines)} Zeilen statt {total_lines}"
    i = 0
    for inv, amounts in cur:
        for amount in amounts:
            total = 0
            for tok in lines[i].split():
                k, c = tok.split("x")
                k, c = int(k), int(c)
                if c not in inv or k <= 0 or k > inv[c]:
                    return f"Zeile {i + 1}: ungueltig {tok}"
                total += k * c
            i += 1
            if total != amount:
                return f"Zeile {i}: Summe {total} statt {amount}"
    return None


def solve(data):
    out = []
    for inv, amounts in parse5(data):
        solver = Solver(inv)
        out += [format_counts(solver.counts(a)) for a in amounts]
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
