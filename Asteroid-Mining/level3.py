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


# ---- Level 3: Input je Asteroid 'W H LIMIT' + (H+2) Raster-Zeilen; W oder H ist 3, Posten irgendwo in Zeile 0.
# Tunnel muss zusammenhaengend sein (an den Posten angeschlossen) und jede minierbare Zelle abdecken
# (Tunnel oder 4er-Nachbar eines Tunnels), hoechstens LIMIT gegrabene Zellen.
def parse_grids(data):
    t = data.split()
    n, pos, res = int(t[0]), 1, []
    for _ in range(n):
        w, h, limit = int(t[pos]), int(t[pos + 1]), int(t[pos + 2])
        grid = [list(row) for row in t[pos + 3:pos + 3 + h + 2]]
        res.append((w, h, limit, grid))
        pos += 3 + h + 2
    return res


def tunnel_cells(w, h, sc):
    """Zellen (r, c) im Raster-Koordinatensystem; sc = Spalte des Postens in Zeile 0. Waehlt die guenstigere Ausrichtung."""
    cands = []
    if w == 3:  # senkrechte Mittelspalte (Spalte 2), Anschluss an den Posten ueber Zeile 1
        cells = {(r, 2) for r in range(1, h + 1)}
        cells.add((1, sc))
        cells.add((1, 2))
        cands.append(cells)
    if h == 3:  # waagerechte Mittelzeile (Zeile 2) ueber die ganze Breite, Anschluss ueber (1, sc)
        cells = {(2, c) for c in range(1, w + 1)}
        cells.add((1, sc))
        cands.append(cells)
    return min(cands, key=len)


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


def solve(data):
    out = []
    for w, h, limit, grid in parse_grids(data):
        sc = grid[0].index(OUTPOST)
        cells = tunnel_cells(w, h, sc)
        err = check(grid, cells, limit)
        if err:
            raise ValueError(err)
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
