import sys
from itertools import permutations, product

BEATS = {"R": "S", "S": "P", "P": "R"}  # Schluessel schlaegt Wert


def winner(a, b):
    if a == b or BEATS[a] == b:
        return a
    return b


def play_round(styles):
    return [winner(styles[i], styles[i + 1]) for i in range(0, len(styles) - 1, 2)]


def tournament(styles, rounds):
    styles = list(styles)
    for _ in range(rounds):
        if len(styles) < 2:
            break
        styles = play_round(styles)
    return "".join(styles)


# ---- Level 3: Aufstellung so bauen, dass nach 2 Runden kein R mehr uebrig ist
# Jeder 4er-Block (Paare (a b)(c d)) liefert genau einen Ueberlebenden.
def best_arrangement(comp, want):
    """Anordnung eines 4er-Blocks (String) mit Ueberlebendem != R (und == want, falls gesetzt)."""
    for perm in sorted(set(permutations(comp))):
        w = tournament(perm, 2)
        if w != "R" and (want is None or w == want):
            return "".join(perm)
    return None


def fill_quads(r, p, s, q):
    """Verteile r,p,s auf q Bloecke, jeder Block mit R braucht ein P. Gibt Block-Strings zurueck oder None."""
    k = -(-r // 3)
    if r and (k > p or k > q):
        return None
    pool = ["P"] * (p - k) + ["S"] * s
    quads = []
    rs = r
    for i in range(q):
        if i < k:
            take = min(3, rs)
            rs -= take
            quads.append(["R"] * take + ["P"])
        else:
            quads.append([])
    for qd in quads:
        while len(qd) < 4:
            qd.append(pool.pop())
    return ["".join(qd) for qd in quads]


def build(m, r, p, s):
    q = m // 4
    for r0, p0, s0 in product(range(5), repeat=3):
        if r0 + p0 + s0 != 4 or s0 < 1 or r0 > r or p0 > p or s0 > s:
            continue
        special = best_arrangement("R" * r0 + "P" * p0 + "S" * s0, "S")
        if not special:
            continue
        rest = fill_quads(r - r0, p - p0, s - s0, q - 1)
        if rest is None:
            continue
        return special + "".join(best_arrangement(x, None) for x in rest)
    raise ValueError(f"keine Loesung fuer {m} {r} {p} {s}")


def build_l4(m, r, p, s):
    """Kette: S*, T_0 (Groesse 1), T_1 (2), ... T_{k-1}. Alle R in Teilbaeumen T_j mit mind. 1 P.
    R-Teilbaum: Paare (R S) vorne (S stirbt an R), dann R, dann P -> Sieger P (P verliert nie gegen R)."""
    k = m.bit_length() - 1
    if s < 1:
        raise ValueError("kein S")
    zmax = min(r, s - 1)
    for mask in range(1 << k):
        js = [j for j in range(k) if mask >> j & 1]
        if r == 0 and js:
            continue
        t = sum(1 << j for j in js)
        c = len(js)
        if t < r or c > p:
            continue
        y = max(c, t - r - zmax)
        z = t - r - y
        if y > p or z < 0 or z > zmax:
            continue
        rr, zz, yy = r, z, y - c
        subs = {}
        for j in js:
            slots = (1 << j) - 1
            zj = min(zz, slots // 2)
            xj = min(rr, slots - zj)
            pj = slots - zj - xj
            rr, zz, yy = rr - xj, zz - zj, yy - pj
            subs[j] = "RS" * zj + "R" * (xj - zj) + "P" * (pj + 1)
        pool = ["P"] * (p - y) + ["S"] * (s - 1 - z)
        parts = ["S"]
        for j in range(k):
            parts.append(subs[j] if j in subs else "".join(pool.pop() for _ in range(1 << j)))
        return "".join(parts)
    raise ValueError(f"keine Loesung fuer {m} {r} {p} {s}")


def validate(inp, out):
    """None wenn ok, sonst Fehlertext."""
    lines = inp.split()
    n, m = int(lines[0]), int(lines[1])
    res = out.split()
    if len(res) != n:
        return f"{len(res)} Zeilen statt {n}"
    for i, line in enumerate(res):
        exp = {c: int(x[:-1]) for x, c in zip(lines[2 + 3 * i:5 + 3 * i], "RPS")}
        if len(line) != m or any(line.count(c) != exp[c] for c in "RPS"):
            return f"Zeile {i + 1}: falsche Anzahl/Laenge"
        w = tournament(line, 99)
        if w != "S":
            return f"Zeile {i + 1}: Sieger {w!r}"
    return None


def solve(data):
    t = data.split()
    n, m = int(t[0]), int(t[1])
    out = []
    for i in range(n):
        r, p, s = (int(x[:-1]) for x in t[2 + 3 * i:5 + 3 * i])
        out.append(build_l4(m, r, p, s))
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
