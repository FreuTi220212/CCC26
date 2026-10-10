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


def validate(inp, out):
    """None wenn ok, sonst Fehlertext."""
    lines = inp.split()
    n, m = int(lines[0]), int(lines[1])
    res = out.split()
    if len(res) != n:
        return f"{len(res)} Zeilen statt {n}"
    for i, line in enumerate(res):
        cnt = {c: int(lines[2 + 3 * i + j][:-1]) for j, c in enumerate("RPS")}
        exp = {c: int(x[:-1]) for x, c in zip(lines[2 + 3 * i:5 + 3 * i], "RPS")}
        if len(line) != m or any(line.count(c) != exp[c] for c in "RPS"):
            return f"Zeile {i + 1}: falsche Anzahl/Laenge"
        w = tournament(line, 2)
        if "R" in w or "S" not in w:
            return f"Zeile {i + 1}: Ueberlebende {w!r}"
    return None


def solve(data):
    t = data.split()
    n, m = int(t[0]), int(t[1])
    out = []
    for i in range(n):
        r, p, s = (int(x[:-1]) for x in t[2 + 3 * i:5 + 3 * i])
        out.append(build(m, r, p, s))
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
