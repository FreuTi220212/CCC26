import os
import subprocess
import sys
import tempfile

LINE = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]  # Pace-Reihenfolge: nur Nachbarn (oder gleich) sind erlaubt
RANK = {p: i for i, p in enumerate(LINE)}
SAFE = 2  # Sicherheitsbereich: Chebyshev-Abstand <= 2 zu einem Asteroiden = Kollision
HERE = os.path.dirname(os.path.abspath(__file__))


def step(pace):
    """(Weg, Zeit) einer Pace: p>0 -> +1 Raum in p; p<0 -> -1 Raum in |p|; 0 -> kein Weg, 1 Zeit."""
    if pace == 0:
        return 0, 1
    return (1 if pace > 0 else -1), abs(pace)


def simulate(paces):
    """Endposition und Gesamtzeit (Start bei Position 0)."""
    pos = time = 0
    for p in paces:
        d, t = step(p)
        pos += d
        time += t
    return pos, time


def valid_sequence(seq):
    if not seq or seq[0] != 0 or seq[-1] != 0:
        return "Start/Ende nicht 0"
    for a, b in zip(seq, seq[1:]):
        if a not in RANK or b not in RANK or abs(RANK[a] - RANK[b]) > 1:
            return f"Pace-Wechsel {a}->{b} nicht erlaubt"
    return None


def trajectory(seq):
    """Position je Zeittick: die Position aendert sich erst am ENDE der Pace-Dauer (von der Plattform bestaetigt:
    die Spring-am-Anfang-Konvention ist zu streng und liess Faelle am Limit scheitern)."""
    pos, ticks = 0, []
    for p in seq:
        d, t = step(p)
        for k in range(t):
            ticks.append(pos + (d if k == t - 1 else 0))
        pos += d
    return ticks


# ---- Level 7: viele Asteroiden, knappes Limit. Die Loesung berechnet Planner.java (gewichtetes A* ueber den vollen
# kinematischen Zustand beider Achsen: Position + Pace-Eintrag-Zustand je Achse, 1 Tick pro Schritt, Heuristik = Zugzahl
# per BFS auf der Sperrkarte). Python ruft es auf und prueft das Ergebnis (validate).
def parse_cases(data):
    """N, dann je Fall 'x,y limit', 'k' und eine Zeile mit k Asteroiden 'ax,ay'."""
    lines = [l for l in data.splitlines() if l.strip()]
    n = int(lines[0])
    res, i = [], 1
    for _ in range(n):
        coords, limit = lines[i].split()
        x, y = (int(v) for v in coords.split(","))
        ast = [tuple(int(v) for v in a.split(",")) for a in lines[i + 2].split()]
        res.append((x, y, int(limit), ast))
        i += 3
    return res


def blocked_cells(asteroids, xlo, xhi, ylo, yhi):
    cells = set()
    for ax, ay in asteroids:
        if xlo - SAFE <= ax <= xhi + SAFE and ylo - SAFE <= ay <= yhi + SAFE:
            for i in range(-SAFE, SAFE + 1):
                for j in range(-SAFE, SAFE + 1):
                    cells.add((ax + i, ay + j))
    return cells


def validate(inp, out):
    """None wenn ok, sonst Fehlertext. Leerzeilen im Output sind erlaubt."""
    cases = parse_cases(inp)
    lines = [l for l in out.splitlines() if l.strip()]
    if len(lines) != 2 * len(cases):
        return f"{len(lines)} Folgen statt {2 * len(cases)}"
    for i, (x, y, limit, ast) in enumerate(cases):
        seqs = []
        for k, target in enumerate((x, y)):
            seq = [int(v) for v in lines[2 * i + k].split()]
            err = valid_sequence(seq)
            if err:
                return f"Fall {i + 1} {'XY'[k]}: {err}"
            pos, time = simulate(seq)
            if pos != target or time > limit:
                return f"Fall {i + 1} {'XY'[k]}: Position {pos} (soll {target}), Zeit {time} (Limit {limit})"
            seqs.append(seq)
        xs, ys = trajectory(seqs[0]), trajectory(seqs[1])
        n = max(len(xs), len(ys))
        xs += [xs[-1]] * (n - len(xs))
        ys += [ys[-1]] * (n - len(ys))
        blocked = blocked_cells(ast, min(xs), max(xs), min(ys), max(ys))
        if any(p in blocked for p in zip(xs, ys)):
            return f"Fall {i + 1}: Kollision"
    return None


def solve(data):
    """Ruft Planner.java auf (kompiliert bei Bedarf). Gewicht/Threads per Umgebungsvariablen CCC_WEIGHT / CCC_THREADS."""
    if not os.path.exists(os.path.join(HERE, "Planner.class")):
        subprocess.run(["javac", "-d", HERE, os.path.join(HERE, "Planner.java")], check=True)
    with tempfile.TemporaryDirectory() as tmp:
        fin, fout = os.path.join(tmp, "in.txt"), os.path.join(tmp, "out.txt")
        with open(fin, "w", encoding="utf-8") as f:
            f.write(data)
        cmd = ["java", "-Xmx3g", "-cp", HERE, "Planner", fin, fout, os.environ.get("CCC_WEIGHT", "1.5"),
               os.environ.get("CCC_THREADS", "4")]
        subprocess.run(cmd, check=True)
        with open(fout, encoding="utf-8") as f:
            return f.read()


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
