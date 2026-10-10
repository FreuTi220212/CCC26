import heapq
import sys

LINE = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]  # Pace-Reihenfolge: nur Nachbarn (oder gleich) sind erlaubt
RANK = {p: i for i, p in enumerate(LINE)}
FORWARD = [0, 5, 4, 3, 2, 1]  # fuer Ziele > 0 reichen diese Paces (negativ: spiegeln)


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


# ---- Level 4: 2D, X- und Y-Folge getrennt, beide innerhalb des Limits (= Optimum). Je Achse kuerzeste Folge per Dijkstra
# ueber Zustaende (Position, Pace); Nachbarschaft wie LINE. Start: Pace 0 (kostet 1 Zeit), Ende: Pace 0 bei Zielposition.
def shortest_table(max_pos):
    """dist[(pos, pace)] und parent fuer alle pos <= max_pos (nur vorwaerts)."""
    start = (0, 0)
    dist, parent = {start: 1}, {start: None}
    heap = [(1, 0, 0)]
    while heap:
        t, pos, pace = heapq.heappop(heap)
        if dist.get((pos, pace), 1 << 60) < t:
            continue
        for nxt in FORWARD:
            if abs(RANK[pace] - RANK[nxt]) > 1:
                continue
            dpos, dt = step(nxt)
            npos = pos + dpos
            if npos > max_pos:
                continue
            nt, state = t + dt, (npos, nxt)
            if nt < dist.get(state, 1 << 60):
                dist[state], parent[state] = nt, (pos, pace)
                heapq.heappush(heap, (nt, npos, nxt))
    return dist, parent


def axis_sequence(d, table):
    """Kuerzeste gueltige Folge (Liste von Paces) zur Position d auf einer Achse."""
    dist, parent = table
    sign = 1 if d >= 0 else -1
    state = (abs(d), 0)
    seq = []
    while state is not None:
        seq.append(state[1])
        state = parent[state]
    seq.reverse()
    if abs(d) == 0:
        return [0]
    return [sign * p for p in seq]


def parse_cases(data):
    """N, dann N Zeilen 'x,y limit'."""
    lines = [l for l in data.splitlines() if l.strip()]
    n = int(lines[0])
    res = []
    for line in lines[1:1 + n]:
        coords, limit = line.split()
        x, y = coords.split(",")
        res.append((int(x), int(y), int(limit)))
    return res


def validate(inp, out):
    """None wenn ok, sonst Fehlertext. Leerzeilen im Output sind erlaubt."""
    cases = parse_cases(inp)
    lines = [l for l in out.splitlines() if l.strip()]
    if len(lines) != 2 * len(cases):
        return f"{len(lines)} Folgen statt {2 * len(cases)}"
    for i, (x, y, limit) in enumerate(cases):
        for axis, target in (("X", x), ("Y", y)):
            seq = [int(v) for v in lines[2 * i + (axis == "Y")].split()]
            err = valid_sequence(seq)
            if err:
                return f"Fall {i + 1} {axis}: {err}"
            pos, time = simulate(seq)
            if pos != target or time > limit:
                return f"Fall {i + 1} {axis}: Position {pos} (soll {target}), Zeit {time} (Limit {limit})"
    return None


def solve(data):
    cases = parse_cases(data)
    table = shortest_table(max(max(abs(x), abs(y)) for x, y, _ in cases))
    blocks = []
    for x, y, _limit in cases:
        blocks.append(" ".join(map(str, axis_sequence(x, table))) + "\n" + " ".join(map(str, axis_sequence(y, table))) + "\n")
    return "\n".join(blocks)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
