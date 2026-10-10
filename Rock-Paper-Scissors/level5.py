import sys

import numpy as np
from scipy.optimize import LinearConstraint, milp

# Stile: R=Rock, P=Paper, S=Scissors, Y=Spock, L=Lizard. Schluessel schlaegt Werte.
BEATS = {"R": "LS", "P": "RY", "S": "PL", "L": "YP", "Y": "SR"}
ORDER = "RPSYL"  # Reihenfolge der Mengen im Input


def winner(a, b):
    if a == b or b in BEATS[a]:
        return a
    return b


def play_round(styles):
    return [winner(styles[i], styles[i + 1]) for i in range(0, len(styles) - 1, 2)]


def tournament(styles, rounds=99):
    styles = list(styles)
    for _ in range(rounds):
        if len(styles) < 2:
            break
        styles = play_round(styles)
    return "".join(styles)


# ---- Level 5: Sieger muss S sein.
# Rueckwaerts gedacht: Start [S]; in jedem Schritt bekommt JEDER vorhandene Kaempfer x einen Gegner z,
# den er schlaegt (oder gleicher Stil) -> Liste verdoppelt sich, Paare (x, z) stehen nebeneinander.
# Nach k Schritten (2^k = M) muessen genau die Anzahlen aus dem Input herauskommen.
# Variablen f[t][(x, z)] = wie viele x in Schritt t einen Gegner z bekommen -> kleines ganzzahliges LP (HiGHS).
PAIRS = [(x, z) for x in ORDER for z in ORDER if x == z or z in BEATS[x]]


def build(m, counts, root="S"):
    k = m.bit_length() - 1
    npair = len(PAIRS)
    nvar = k * npair
    idx = lambda t, p: t * npair + p
    rows, rhs = [], []
    # Schritt t: jeder x (a_x(t) Stueck) bekommt genau einen Gegner. a_x(t) = [x==root] + Zugaenge aus Schritten < t
    for t in range(k):
        for x in ORDER:
            row = np.zeros(nvar)
            for p, (px, pz) in enumerate(PAIRS):
                if px == x:
                    row[idx(t, p)] += 1
                if pz == x:
                    for t2 in range(t):
                        row[idx(t2, p)] -= 1
            rows.append(row)
            rhs.append(1 if x == root else 0)
    # Summe der Zugaenge je Stil = Input - Wurzel
    for z in ORDER:
        row = np.zeros(nvar)
        for p, (px, pz) in enumerate(PAIRS):
            if pz == z:
                for t in range(k):
                    row[idx(t, p)] += 1
        rows.append(row)
        rhs.append(counts[z] - (1 if z == root else 0))
    res = milp(
        c=np.zeros(nvar),
        constraints=LinearConstraint(np.array(rows), rhs, rhs),
        integrality=np.ones(nvar),
        bounds=(0, np.inf),
    )
    if res.x is None:
        raise ValueError(f"keine Loesung fuer {m} {counts}")
    f = np.rint(res.x).astype(int)
    cur = [root]
    for t in range(k):
        left = {pr: f[idx(t, p)] for p, pr in enumerate(PAIRS)}
        new = []
        for x in cur:
            z = next(z for z in ORDER if left.get((x, z), 0) > 0)
            left[(x, z)] -= 1
            new += [x, z]
        cur = new
    return "".join(cur)


def validate(inp, out):
    """None wenn ok, sonst Fehlertext."""
    t = inp.split()
    n, m = int(t[0]), int(t[1])
    res = out.split()
    if len(res) != n:
        return f"{len(res)} Zeilen statt {n}"
    for i, line in enumerate(res):
        exp = {c: int(x[:-1]) for x, c in zip(t[2 + 5 * i:7 + 5 * i], ORDER)}
        if len(line) != m or any(line.count(c) != exp[c] for c in ORDER):
            return f"Zeile {i + 1}: falsche Anzahl/Laenge"
        w = tournament(line)
        if w != "S":
            return f"Zeile {i + 1}: Sieger {w!r}"
    return None


def solve(data):
    t = data.split()
    n, m = int(t[0]), int(t[1])
    out = []
    for i in range(n):
        counts = {c: int(x[:-1]) for x, c in zip(t[2 + 5 * i:7 + 5 * i], ORDER)}
        out.append(build(m, counts))
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
