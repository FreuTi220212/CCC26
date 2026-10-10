import sys

BEDROCK, MINABLE, OUTPOST, TUNNEL = "#", ":", "S", "X"


# ---- Level 1 (zur Erweiterung behalten)
def render(width, height):
    """Asteroid: minierbares Rechteck width x height, ringsum eine Schicht Grundgestein."""
    border = BEDROCK * (width + 2)
    row = BEDROCK + MINABLE * width + BEDROCK
    return [border] + [row] * height + [border]


# ---- Level 2: Input ab hier: N, je Asteroid 'W H' + (H+2) Zeilen Raster
def parse_grids(data):
    t = data.split()
    n, pos, res = int(t[0]), 1, []
    for _ in range(n):
        w, h = int(t[pos]), int(t[pos + 1])
        grid = [list(row) for row in t[pos + 2:pos + 2 + h + 2]]
        res.append((w, h, grid))
        pos += 2 + h + 2
    return res


def dig_straight_down(grid):
    """Tunnel unter dem Aussenposten senkrecht nach unten, nur durch minierbare Zellen (vor dem Grundgestein)."""
    for c, ch in enumerate(grid[0]):
        if ch == OUTPOST:
            r = 1
            while r < len(grid) and grid[r][c] == MINABLE:
                grid[r][c] = TUNNEL
                r += 1
    return grid


def solve(data):
    out = []
    for _, _, grid in parse_grids(data):
        out.append("\n".join("".join(r) for r in dig_straight_down(grid)) + "\n\n")  # Leerzeile nach JEDEM Asteroiden
    return "".join(out)


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
