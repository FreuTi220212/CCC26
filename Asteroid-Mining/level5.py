import sys

BEDROCK, MINABLE, OUTPOST, TUNNEL = "#", ":", "S", "X"
INF = 10 ** 9


# ---- Level 1/2 (zur Erweiterung behalten)
def render(width, height):
    """Asteroid: minierbares Rechteck width x height, ringsum eine Schicht Grundgestein."""
    border = BEDROCK * (width + 2)
    row = BEDROCK + MINABLE * width + BEDROCK
    return [border] + [row] * height + [border]


def dig_straight_down(grid):
    """Level 2: Tunnel senkrecht unter dem Aussenposten durch alle minierbaren Zellen."""
    for c, ch in enumerate(grid[0]):
        if ch == OUTPOST:
            r = 1
            while r < len(grid) and grid[r][c] == MINABLE:
                grid[r][c] = TUNNEL
                r += 1
    return grid


# ---- Level 3-5: Input je Asteroid 'W H LIMIT' + (H+2) Raster-Zeilen. Posten irgendwo in Zeile 0.
# Tunnel zusammenhaengend (am Posten), jede minierbare Zelle Tunnel oder 4er-Nachbar eines Tunnels, max. LIMIT Zellen.
# Level 3: W oder H = 3. Level 4: W oder H durch 3 teilbar, Limit = Optimum + 1. Level 5: beliebig, Limit = Optimum.
def parse_grids(data):
    t = data.split()
    n, pos, res = int(t[0]), 1, []
    for _ in range(n):
        w, h, limit = int(t[pos]), int(t[pos + 1]), int(t[pos + 2])
        grid = [list(row) for row in t[pos + 3:pos + 3 + h + 2]]
        res.append((w, h, limit, grid))
        pos += 3 + h + 2
    return res


def neighbours(r, c):
    return ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))


def check(grid, tunnels, limit):
    """None wenn gueltig, sonst Fehlertext. grid = Original-Raster (mit ':' und 'S')."""
    h, w = len(grid), len(grid[0])
    start = next((0, c) for c in range(w) if grid[0][c] == OUTPOST)
    if len(tunnels) > limit:
        return f"{len(tunnels)} Tunnelzellen > Limit {limit}"
    for r, c in tunnels:
        if grid[r][c] != MINABLE:
            return f"Tunnel auf {grid[r][c]!r} bei {(r, c)}"
    seen, stack = set(), [start]
    while stack:
        cur = stack.pop()
        for nb in neighbours(*cur):
            if nb in tunnels and nb not in seen:
                seen.add(nb)
                stack.append(nb)
    if seen != set(tunnels):
        return "Tunnel nicht zusammenhaengend / nicht am Posten"
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            if (r, c) not in tunnels and not any(nb in tunnels for nb in neighbours(r, c)):
                return f"Zelle {(r, c)} nicht entdeckt"
    return None


# ---- Level 5: Kamm = Rueckgrat (am Rand oder 1 Zeile/Spalte davon) + Zinken auf EINER Seite.
# Seite der Hoehe H (Zinkenlaenge 0..H), Rueckgratlaenge L: Zinkenlaenge u_j in {0, H-1, H} je Spalte j.
# H = voller Zinken (deckt 3 Spalten), H-1 deckt nur die eigene Spalte, 0 braucht einen vollen Nachbarn.
# Das Rueckgrat darf an den Enden eine Zelle kuerzer sein (skipL/skipR), wenn dort u=0 (Nachbar-Zinken deckt ab).
# Mit exaktem ILP (scipy, kleine Raster) abgeglichen: die Limits der Aufgabe sind das echte Optimum.
_dp_cache = {}


def region_dp(H, L, mode=None, par=0, skip_l=False, skip_r=False):
    """Min. Zinkenzellen einer Seite. mode None: ohne Anschluss. 'top': Zinken j* voll (u=H), Kosten |par-j*|
    (Posten ueber Spalte par am Rand). 'end': Anschlusszeile j*, Kosten (j*-1)+max(0, par-u_j*).
    skip_l/skip_r: u_1 bzw. u_L muss 0 sein (Rueckgrat dort gekuerzt, dort kein Anschluss moeglich).
    Gibt (Kosten, [u_1..u_L], j*) zurueck."""
    key = (H, L, mode, par, skip_l, skip_r)
    if key in _dp_cache:
        return _dp_cache[key]
    o = sorted({0, max(H - 1, 0), H})

    def need(b):
        return H >= 2 and b <= H - 2

    def allowed(u, j):
        if j == 1 and skip_l:
            return u == 0
        if j == L and skip_r:
            return u == 0
        return True

    def marks(u, j, f):
        """Liste (neues_flag, Zusatzkosten)."""
        res = [(f, 0)]
        if mode and not f:
            if mode == "top" and u == H and H >= 1:
                res.append((1, abs(par - j)))
            elif mode == "end" and not (j == 1 and skip_l) and not (j == L and skip_r):
                res.append((1, (j - 1) + max(0, par - u)))
        return res

    f0 = 1 if mode is None else 0
    layers = []
    cur = {}
    for u in o:
        if not allowed(u, 1):
            continue
        for nf, mc in marks(u, 1, f0):
            st = (-1, u, nf)
            if st not in cur or u + mc < cur[st][0]:
                cur[st] = (u + mc, None, nf != f0)
    layers.append(cur)
    for j in range(2, L + 1):
        nxt = {}
        for (a, b, f), (cost, _, _) in cur.items():
            for c in o:
                if not allowed(c, j) or (need(b) and not (a == H or c == H)):
                    continue
                for nf, mc in marks(c, j, f):
                    st = (b, c, nf)
                    nc = cost + c + mc
                    if st not in nxt or nc < nxt[st][0]:
                        nxt[st] = (nc, (a, b, f), nf != f)
        layers.append(nxt)
        cur = nxt
    best, bst = INF, None
    for (a, b, f), (cost, _, _) in cur.items():
        if f == 1 and (not need(b) or a == H) and cost < best:
            best, bst = cost, (a, b, f)
    if bst is None:
        res = (INF, [], None)
    else:
        us, jstar, st = [0] * (L + 1), None, bst
        for j in range(L, 0, -1):
            cost, prev, marked = layers[j - 1][st]
            us[j] = st[1]
            if marked:
                jstar = j
            st = prev
        res = (best, us, jstar)
    _dp_cache[key] = res
    return res


ZERO = (0, None, None)


def teeth_lb(H, L):
    """Untere Schranke fuer die Zinkenkosten einer Seite (ohne Anschluss/Kuerzungen), gecacht."""
    return region_dp(H, L)[0] if H >= 2 else 0


def build(w, h, sc):
    """Beste Kamm-Loesung (Menge von (r, c)): waagerechtes oder senkrechtes Rueckgrat am Rand (oder 1 davon entfernt).
    Kandidaten werden nach unterer Schranke sortiert und erst bei Bedarf per DP genau bewertet."""
    jobs = []  # (lb, orientierung, p, sl, sr)
    L = w
    for p in sorted({q for q in (1, 2, h - 1, h) if 1 <= q <= h}):
        A, B = p - 1, h - p
        for sl in (0, 1):
            for sr in (0, 1):
                if (sl or sr) and (A == 1 or B == 1):
                    continue
                if p == 1 and ((sl and sc == 1) or (sr and sc == L)):
                    continue
                if A >= 2 and B >= 2:
                    continue
                lb = (L - sl - sr) + (1 if A == 1 else 0) + teeth_lb(max(A, B), L)
                jobs.append((lb, "H", p, sl, sr))
    L = h
    for p in sorted({q for q in (1, 2, w - 1, w) if 1 <= q <= w}):
        A, B = p - 1, w - p
        for sl in (0, 1):
            for sr in (0, 1):
                if (sl or sr) and (A == 1 or B == 1):
                    continue
                if sc == p and sl:
                    continue
                if A >= 2 and B >= 2:
                    continue
                lb = (L - sl - sr) + teeth_lb(max(A, B), L)
                jobs.append((lb, "V", p, sl, sr))
    jobs.sort(key=lambda x: x[0])
    best_cost, best_cells = INF, None
    for lb, orient, p, sl, sr in jobs:
        if lb >= best_cost:
            break
        res = eval_H(w, h, sc, p, sl, sr) if orient == "H" else eval_V(w, h, sc, p, sl, sr)
        if res and res[0] < best_cost:
            best_cost, best_cells = res
    return best_cells


def eval_H(w, h, sc, p, sl, sr):
    """Waagerechtes Rueckgrat in Zeile p (Spalten 1+sl..w-sr), Zinken senkrecht, Posten oben ueber Spalte sc."""
    L = w
    A, B = p - 1, h - p
    cells = {(p, c) for c in range(1 + sl, L - sr + 1)}
    cost = len(cells)
    extra = None
    if A == 0:
        reg, sgn = region_dp(B, L, None, 0, bool(sl), bool(sr)), 1
    elif A == 1:
        reg = region_dp(B, L, None, 0) if B >= 2 else ZERO
        sgn, extra = 1, ("cell", (1, sc))
        cost += 1
    else:
        reg, sgn = region_dp(A, L, "top", sc, bool(sl), bool(sr)), -1
        extra = ("top", reg[2])
    if reg[0] >= INF:
        return None
    cost += reg[0]
    us = reg[1] or [0] * (L + 1)
    for c in range(1, L + 1):
        cells |= {(p + sgn * k, c) for k in range(1, us[c] + 1)}
    if extra:
        if extra[0] == "cell":
            cells.add(extra[1])
        else:
            j = extra[1]
            cells |= {(1, c) for c in range(min(sc, j), max(sc, j) + 1)}
    return cost, cells


def eval_V(w, h, sc, p, sl, sr):
    """Senkrechtes Rueckgrat in Spalte p (Zeilen 1+sl..h-sr), Zinken waagerecht, Posten ueber Zeile 1, Spalte sc."""
    L = h
    A, B = p - 1, w - p  # links, rechts
    delta = abs(sc - p)
    cells = {(r, p) for r in range(1 + sl, L - sr + 1)}
    cost = len(cells)
    nt = ("l", A) if A >= 2 else ("r", B) if B >= 2 else None
    s_side = None if delta == 0 else ("l" if sc < p else "r")
    if nt:
        mode = "end" if s_side == nt[0] else None
        reg = region_dp(nt[1], L, mode, delta if mode else 0, bool(sl), bool(sr))
        if reg[0] >= INF:
            return None
        cost += reg[0]
        us, jstar = reg[1], reg[2]
        d = -1 if nt[0] == "l" else 1
        for r in range(1, L + 1):
            cells |= {(r, p + d * k) for k in range(1, us[r] + 1)}
        if mode:
            cells |= {(r, sc) for r in range(1, jstar)}
            cells |= {(jstar, p + d * k) for k in range(us[jstar] + 1, delta + 1)}
    if delta and s_side != (nt[0] if nt else None):
        cells.add((1, sc))  # Posten auf der Seite der Hoehe 1 (delta == 1)
        cost += 1
    return cost, cells


def solve(data):
    out = []
    for w, h, limit, grid in parse_grids(data):
        sc = grid[0].index(OUTPOST)
        cells = build(w, h, sc)
        err = check(grid, cells, limit)
        if err:
            raise ValueError(f"{w}x{h} sc={sc}: {err}")
        for r, c in cells:
            grid[r][c] = TUNNEL
        out.append("\n".join("".join(row) for row in grid) + "\n\n")  # Leerzeile nach JEDEM Asteroiden
    return "".join(out)


def validate(inp, out):
    """None wenn ok, sonst Fehlertext."""
    asteroids = parse_grids(inp)
    blocks = out.strip("\n").split("\n\n")
    if len(blocks) != len(asteroids):
        return f"{len(blocks)} Bloecke statt {len(asteroids)}"
    for i, ((w, h, limit, grid), block) in enumerate(zip(asteroids, blocks)):
        rows = block.split("\n")
        if len(rows) != h + 2 or any(len(r) != w + 2 for r in rows):
            return f"Asteroid {i + 1}: falsche Groesse"
        tunnels = set()
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch == TUNNEL:
                    tunnels.add((r, c))
                elif ch != grid[r][c]:
                    return f"Asteroid {i + 1}: Zelle {(r, c)} veraendert"
        err = check(grid, tunnels, limit)
        if err:
            return f"Asteroid {i + 1}: {err}"
    return None


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
