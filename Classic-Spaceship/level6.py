import heapq
import sys

LINE = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]  # Pace-Reihenfolge: nur Nachbarn (oder gleich) sind erlaubt
RANK = {p: i for i, p in enumerate(LINE)}
FORWARD = [0, 5, 4, 3, 2, 1]  # fuer Ziele > 0 reichen diese Paces (negativ: spiegeln)
SAFE = 2  # Sicherheitsbereich: Quadrat mit Radius 2 um das Schiff (Chebyshev-Abstand <= 2 = Kollision)
TURN_COST = 14  # Richtungswechsel = anhalten + neu anfahren, grob geschaetzt


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


# ---- Level 4: kuerzeste Folge je Achse per Dijkstra ueber (Position, Pace)
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
    _, parent = table
    sign = 1 if d >= 0 else -1
    if d == 0:
        return [0]
    state, seq = (abs(d), 0), []
    while state is not None:
        seq.append(state[1])
        state = parent[state]
    seq.reverse()
    return [sign * p for p in seq]


# ---- Level 5: ein ruhender Asteroid. Chebyshev-Abstand zum Schiff muss > 2 bleiben.
# Weg auf Gitterpunkten (Dijkstra mit Richtungswechsel-Strafe), danach Achsen nacheinander bewegen: waehrend eine
# Achse faehrt, steht die andere (Nullen als Wartezeit). So ist die Position zu jedem Zeitpunkt eindeutig.
def parse_cases(data):
    """N, dann je Fall 'x,y limit' und 'ax,ay'."""
    lines = [l for l in data.splitlines() if l.strip()]
    n = int(lines[0])
    res = []
    for i in range(n):
        coords, limit = lines[1 + 2 * i].split()
        x, y = (int(v) for v in coords.split(","))
        ax, ay = (int(v) for v in lines[2 + 2 * i].strip().split(","))
        res.append((x, y, int(limit), ax, ay))
    return res


def l_path_free(points, asteroid):
    """Alle Gitterpunkte entlang der Eckpunkte-Folge `points` (achsparallele Teilstuecke) ausserhalb des Sicherheitsbereichs?"""
    ax, ay = asteroid
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        n = abs(x1 - x0) + abs(y1 - y0)
        sx, sy = (x1 > x0) - (x1 < x0), (y1 > y0) - (y1 < y0)
        for k in range(n + 1):
            if max(abs(x0 + sx * k - ax), abs(y0 + sy * k - ay)) <= SAFE:
                return False
    return True


def plan_path(target, asteroid):
    """Liste von Segmenten (achse, vorzeichen, laenge) von (0,0) zum Ziel, ohne den Sicherheitsbereich zu betreten.
    Erst die beiden L-Wege (schnell), nur bei Blockade Dijkstra auf dem Gitter."""
    tx, ty = target
    ax, ay = asteroid
    for corner in ((tx, 0), (0, ty)):
        pts = [(0, 0), corner, (tx, ty)]
        if l_path_free(pts, asteroid):
            return [[axis, sign, length] for axis, sign, length in (
                (0, (tx > 0) - (tx < 0), abs(tx)), (1, (ty > 0) - (ty < 0), abs(ty))) if length] if corner == (tx, 0) else                 [[axis, sign, length] for axis, sign, length in (
                    (1, (ty > 0) - (ty < 0), abs(ty)), (0, (tx > 0) - (tx < 0), abs(tx))) if length]
    m = SAFE + 2
    xlo, xhi = min(0, tx, ax) - m, max(0, tx, ax) + m
    ylo, yhi = min(0, ty, ay) - m, max(0, ty, ay) + m
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def blocked(x, y):
        return max(abs(x - ax), abs(y - ay)) <= SAFE

    start = (0, 0, -1)
    dist, parent = {start: 0}, {start: None}
    heap = [(0, 0, 0, -1)]
    goal = None
    while heap:
        c, x, y, d = heapq.heappop(heap)
        if dist.get((x, y, d), 1 << 60) < c:
            continue
        if (x, y) == (tx, ty):
            goal = (x, y, d)
            break
        for nd, (dx, dy) in enumerate(dirs):
            nx, ny = x + dx, y + dy
            if not (xlo <= nx <= xhi and ylo <= ny <= yhi) or blocked(nx, ny):
                continue
            nc = c + 1 + (TURN_COST if d != -1 and nd != d else 0)
            st = (nx, ny, nd)
            if nc < dist.get(st, 1 << 60):
                dist[st], parent[st] = nc, (x, y, d)
                heapq.heappush(heap, (nc, nx, ny, nd))
    if goal is None:
        raise ValueError(f"kein Weg {target} / Asteroid {asteroid}")
    dseq, st = [], goal
    while parent[st] is not None:
        dseq.append(st[2])
        st = parent[st]
    dseq.reverse()
    segs = []
    for d in dseq:
        axis, sign = (0, dirs[d][0]) if dirs[d][0] else (1, dirs[d][1])
        if segs and segs[-1][0] == axis and segs[-1][1] == sign:
            segs[-1][2] += 1
        else:
            segs.append([axis, sign, 1])
    return segs


def build_sequences(segs, table):
    """X- und Y-Folge: je Segment faehrt eine Achse, die andere wartet mit Nullen (gleiche Dauer)."""
    seqs = [[0], [0]]
    first = True
    for axis, sign, length in segs:
        prof = [sign * abs(p) for p in axis_sequence(length, table)]
        t = simulate(prof)[1]
        for a in (0, 1):
            part = prof if a == axis else [0] * t
            seqs[a] = (part if first else seqs[a] + part)
        first = False
    return seqs


def trajectory(seq, jump_at_start):
    """Position je Zeittick (Tick i = Zeitintervall [i, i+1)). Sprung am Anfang oder am Ende der Pace-Dauer."""
    pos, ticks = 0, []
    for p in seq:
        d, t = step(p)
        for k in range(t):
            ticks.append(pos + (d if (jump_at_start or k == t - 1) else 0))
        pos += d
    return ticks


def collision_free(seq_x, seq_y, asteroid, start=(0, 0)):
    """Kein Tick mit Chebyshev-Abstand <= SAFE (Sprung am Anfang UND am Ende der Pace-Dauer geprueft)."""
    ax, ay = asteroid
    x0, y0 = start
    for jump_at_start in (True, False):
        xs, ys = trajectory(seq_x, jump_at_start), trajectory(seq_y, jump_at_start)
        n = max(len(xs), len(ys))
        xs += [xs[-1]] * (n - len(xs))
        ys += [ys[-1]] * (n - len(ys))
        for x, y in zip(xs, ys):
            if max(abs(x0 + x - ax), abs(y0 + y - ay)) <= SAFE:
                return False
        if max(abs(x0 + xs[0] - ax), abs(y0 + ys[0] - ay)) <= SAFE:
            return False
    return True


def validate(inp, out):
    """None wenn ok, sonst Fehlertext. Leerzeilen im Output sind erlaubt."""
    cases = parse_cases(inp)
    lines = [l for l in out.splitlines() if l.strip()]
    if len(lines) != 2 * len(cases):
        return f"{len(lines)} Folgen statt {2 * len(cases)}"
    for i, (x, y, limit, ax, ay) in enumerate(cases):
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
        if not collision_free(seqs[0], seqs[1], (ax, ay)):
            return f"Fall {i + 1}: Kollision mit Asteroid {(ax, ay)}"
    return None


# ---- Level 6: Limit deutlich kuerzer (nicht optimal). Beide Achsen gleichzeitig fahren (Optimalfolgen), eine Achse
# ggf. verzoegert starten (Nullen vorn); erster kollisionsfreier Kandidat mit kleinster Gesamtzeit gewinnt.
# Sonst Rueckfall auf den sequentiellen Umweg aus Level 5.
def makespan(sx, sy):
    return max(simulate(sx)[1], simulate(sy)[1])


def parallel_candidates(x, y, table, max_delay=60):
    bx, by = axis_sequence(x, table), axis_sequence(y, table)
    cands = [(makespan(bx, by), [0] * 0, bx, by)]
    for d in range(1, max_delay + 1):
        cands.append((makespan([0] * d + bx, by), 0, [0] * d + bx, by))
        cands.append((makespan(bx, [0] * d + by), 0, bx, [0] * d + by))
    cands.sort(key=lambda c: c[0])
    return [(c[2], c[3]) for c in cands]


def leg_sequences(dx, dy, table):
    """Beide Achsen gleichzeitig (Optimalfolgen), die kuerzere mit Nullen auf gleiche Dauer aufgefuellt."""
    bx, by = axis_sequence(dx, table), axis_sequence(dy, table)
    tx, ty = simulate(bx)[1], simulate(by)[1]
    return bx + [0] * (ty - tx if ty > tx else 0), by + [0] * (tx - ty if tx > ty else 0)


def waypoint_candidates(target, asteroid):
    """Punkte rund um den Sicherheitsbereich (Abstand SAFE+1), von denen aus man gut vorbeikommt."""
    tx, ty = target
    ax, ay = asteroid
    r = SAFE + 1
    pts = {(ax + sx * r, ay + sy * r) for sx in (-1, 0, 1) for sy in (-1, 0, 1) if (sx, sy) != (0, 0)}
    pts |= {(ax + sx * r, ty) for sx in (-1, 1)} | {(ax + sx * r, 0) for sx in (-1, 1)}
    pts |= {(tx, ay + sy * r) for sy in (-1, 1)} | {(0, ay + sy * r) for sy in (-1, 1)}
    return [p for p in pts if max(abs(p[0] - ax), abs(p[1] - ay)) > SAFE and p not in ((0, 0), (tx, ty))]


def route_sequences(points, table):
    """Folgen fuer den Weg ueber `points` ([(0,0), w1, ..., ziel]); jedes Teilstueck parallel in beiden Achsen."""
    sx, sy = [0], [0]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        lx, ly = leg_sequences(x1 - x0, y1 - y0, table)
        sx, sy = sx + lx, sy + ly
    return sx, sy


def best_leg(start, dx, dy, asteroid, table, budget, max_delay=30):
    """Teilstueck mit kleinster Dauer <= budget, kollisionsfrei; eine Achse darf verzoegert starten."""
    bx, by = axis_sequence(dx, table), axis_sequence(dy, table)
    tx, ty = simulate(bx)[1], simulate(by)[1]
    cands = [(max(tx, ty), 0, 0)]
    for d in range(1, max_delay + 1):
        cands.append((max(tx + d, ty), d, 0))
        cands.append((max(tx, ty + d), 0, d))
    for t, dxl, dyl in sorted(cands):
        if t > budget:
            return None
        sx, sy = [0] * dxl + bx, [0] * dyl + by
        tx2, ty2 = simulate(sx)[1], simulate(sy)[1]
        sx, sy = sx + [0] * max(0, ty2 - tx2), sy + [0] * max(0, tx2 - ty2)
        if collision_free(sx, sy, asteroid, start):
            return sx, sy
    return None


def route_best(points, asteroid, table, limit):
    """Zusammengesetzte Folgen fuer die Route (jedes Teilstueck mit Verzoegerungssuche) oder None wenn > limit."""
    sx, sy, used = [0], [0], 1
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        leg = best_leg((x0, y0), x1 - x0, y1 - y0, asteroid, table, limit - used)
        if leg is None:
            return None
        sx, sy = sx + leg[0], sy + leg[1]
        used += simulate(leg[0])[1]
    return (sx, sy) if used <= limit else None


def excursion_solution(x, y, ax, ay, limit, table):
    """Eine Achse faehrt unveraendert (optimal, evtl. verzoegert), die andere macht einen Abstecher zu einer Seite des
    Sicherheitsbereichs, wartet h Ticks und faehrt dann zum Ziel; beide Achsen laufen dabei gleichzeitig."""
    targets, ast = (x, y), (ax, ay)
    for main in (0, 1):
        side = 1 - main
        main_seq = axis_sequence(targets[main], table)
        t_main = simulate(main_seq)[1]
        offsets = [ast[side] + s * r for s in (-1, 1) for r in (SAFE + 1, SAFE + 2)]
        cands = []
        for off in offsets:
            first = axis_sequence(off, table)
            second = axis_sequence(targets[side] - off, table)
            t_side = simulate(first)[1] + simulate(second)[1]
            for h in range(0, 60):
                for d in range(0, 12):
                    cost = max(t_main + d, t_side + h)
                    if cost <= limit:
                        cands.append((cost, off, h, d, first, second))
        for cost, off, h, d, first, second in sorted(cands, key=lambda c: c[0]):
            side_seq = first + [0] * h + second
            m_seq = [0] * d + main_seq
            sx, sy = (m_seq, side_seq) if main == 0 else (side_seq, m_seq)
            if collision_free(sx, sy, ast):
                return sx, sy
    return None


def best_solution(x, y, ax, ay, limit, table):
    """Erst direkt (mit Startverzoegerung), dann ueber 1, dann 2 Wegpunkte; erste gueltige Loesung innerhalb des Limits."""
    if (x, y) == (0, 0):
        return [0], [0]
    for sx, sy in parallel_candidates(x, y, table):
        if makespan(sx, sy) <= limit and collision_free(sx, sy, (ax, ay)):
            return sx, sy
    res = excursion_solution(x, y, ax, ay, limit, table)
    if res:
        return res
    wps = waypoint_candidates((x, y), (ax, ay))
    for routes in ([[w] for w in wps], [[w1, w2] for w1 in wps for w2 in wps if w1 != w2]):
        scored = []
        for mid in routes:
            pts = [(0, 0)] + mid + [(x, y)]
            sx, sy = route_sequences(pts, table)
            scored.append((makespan(sx, sy), pts))
        for t, pts in sorted(scored, key=lambda c: c[0]):
            if t > limit:
                break
            res = route_best(pts, (ax, ay), table, limit)
            if res:
                return res
    return build_sequences(plan_path((x, y), (ax, ay)), table)


def solve(data):
    cases = parse_cases(data)
    table = shortest_table(2 * (max(max(abs(x), abs(y)) for x, y, *_ in cases) + 10))
    blocks = []
    for x, y, limit, ax, ay in cases:
        sx, sy = best_solution(x, y, ax, ay, limit, table)
        blocks.append(" ".join(map(str, sx)) + "\n" + " ".join(map(str, sy)) + "\n")
    return "\n".join(blocks)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
