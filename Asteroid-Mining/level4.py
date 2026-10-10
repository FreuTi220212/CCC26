import sys

BEDROCK, MINABLE, OUTPOST, TUNNEL = "#", ":", "S", "X"


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


# ---- Level 3/4: Input je Asteroid 'W H LIMIT' + (H+2) Raster-Zeilen. Posten irgendwo in Zeile 0.
# Tunnel zusammenhaengend (am Posten), jede minierbare Zelle Tunnel oder 4er-Nachbar eines Tunnels, max. LIMIT Zellen.
# Level 3: W oder H = 3. Level 4: W oder H durch 3 teilbar, Limit = Optimum + 1.
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


def connect(cells, sc):
    """Anschluss an den Posten: kuerzester (L-foermiger) Weg von (1, sc) zur naechsten Kammzelle.
    Liegt (2, sc) schon im Kamm (Zinken), kostet der Anschluss nur 1 Zelle."""
    if (1, sc) in cells:
        return cells
    tr, tc = min(cells, key=lambda p: abs(p[0] - 1) + abs(p[1] - sc))
    path = {(r, sc) for r in range(1, tr + 1)} | {(tr, c) for c in range(min(sc, tc), max(sc, tc) + 1)}
    return cells | (path - {(tr, tc)} if (tr, tc) in cells else path)


def comb(rows, cols, sc, spine_pos):
    """Kamm: senkrechtes Rueckgrat (Spalte spine_pos) ueber die volle Hoehe, waagerechte Zinken in den
    Dreiergruppen-Mitten (Zeilen 2, 5, 8, ...) bis zum Rand, dann Anschluss an den Posten."""
    cells = set()
    cs = spine_pos
    cells |= {(r, cs) for r in range(1, rows + 1)}
    for t in range(2, rows + 1, 3):
        if cs - 1 >= 2:
            cells |= {(t, c) for c in range(1, cs)}
        if cols - cs >= 2:
            cells |= {(t, c) for c in range(cs + 1, cols + 1)}
    return connect(cells, sc)


def candidates(w, h, sc):
    """Alle Kamm-Kandidaten als Mengen von (r, c)."""
    out = []
    # Nur sinnvolle Rueckgrat-Positionen (Rand-nah = wenig Zinkenlaenge, oder nahe am Posten), sonst viel zu langsam
    cols = sorted({p for p in (1, 2, 3, w - 2, w - 1, w, sc - 1, sc, sc + 1) if 1 <= p <= w})
    rows = sorted({p for p in (1, 2, 3, h - 2, h - 1, h) if 1 <= p <= h})
    if h % 3 == 0:  # senkrechtes Rueckgrat
        for cs in cols:
            out.append(comb(h, w, sc, cs))
    if w % 3 == 0:  # waagerechtes Rueckgrat in Zeile rs; Zinken senkrecht in Spalten 2, 5, 8, ...
        for rs in rows:
            cells = {(rs, c) for c in range(1, w + 1)}
            for t in range(2, w + 1, 3):
                if rs - 1 >= 2:
                    cells |= {(r, t) for r in range(1, rs)}
                if h - rs >= 2:
                    cells |= {(r, t) for r in range(rs + 1, h + 1)}
            out.append(connect(cells, sc))
    return out


def best_tunnel(w, h, sc, grid, limit):
    for cells in sorted(candidates(w, h, sc), key=len):  # kleinste zuerst, nur den ersten gueltigen pruefen
        if check(grid, cells, 10 ** 9) is None:
            return cells
    return None


def solve(data):
    out = []
    for w, h, limit, grid in parse_grids(data):
        sc = grid[0].index(OUTPOST)
        cells = best_tunnel(w, h, sc, grid, limit)
        err = check(grid, cells, limit) if cells else "kein Kandidat"
        if err:
            raise ValueError(f"{w}x{h} Limit {limit}: {err} (best {len(cells) if cells else None})")
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
