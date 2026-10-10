import sys

LINE = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]  # Pace-Reihenfolge: nur Nachbarn (oder gleich) sind erlaubt
RANK = {p: i for i, p in enumerate(LINE)}


def parse(data):
    """N, dann N Zeilen mit Pace-Werten."""
    lines = data.splitlines()
    n = int(lines[0])
    return [[int(x) for x in line.split()] for line in lines[1:1 + n]]


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


# ---- Level 3: Sequenz zu Station x mit Zeitlimit. Start/Ende mit 0, nur schrittweise Pace-Aenderung (LINE).
def profile(steps, peak):
    """Positive Pace-Folge mit genau `steps` Schritten: 5,4,..,peak, (Reise mit peak), peak+1,..,5. None wenn zu kurz."""
    up = list(range(5, peak - 1, -1))
    down = list(range(peak + 1, 6))
    cruise = steps - len(up) - len(down)
    if cruise < 0:
        return None
    return up + [peak] * cruise + down


def best_sequence(x):
    """Schnellste Folge dieser Familie (Spitzen-Pace 1..5) zu Position x."""
    if x == 0:
        return [0, 0]
    sign = 1 if x > 0 else -1
    best = None
    for peak in range(1, 6):
        seq = profile(abs(x), peak)
        if seq and (best is None or sum(seq) < sum(best)):
            best = seq
    return [0] + [sign * p for p in best] + [0]


def valid_sequence(seq):
    if not seq or seq[0] != 0 or seq[-1] != 0:
        return "Start/Ende nicht 0"
    for a, b in zip(seq, seq[1:]):
        if a not in RANK or b not in RANK or abs(RANK[a] - RANK[b]) > 1:
            return f"Pace-Wechsel {a}->{b} nicht erlaubt"
    return None


def validate(inp, out):
    """None wenn ok, sonst Fehlertext."""
    cases = parse(inp)
    lines = out.strip("\n").split("\n")
    if len(lines) != len(cases):
        return f"{len(lines)} Zeilen statt {len(cases)}"
    for i, (case, line) in enumerate(zip(cases, lines)):
        x, limit = case
        seq = [int(v) for v in line.split()]
        err = valid_sequence(seq)
        if err:
            return f"Zeile {i + 1}: {err}"
        pos, time = simulate(seq)
        if pos != x or time > limit:
            return f"Zeile {i + 1}: Position {pos} (soll {x}), Zeit {time} (Limit {limit})"
    return None


def solve(data):
    return "\n".join(" ".join(map(str, best_sequence(x))) for x, _limit in parse(data)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
