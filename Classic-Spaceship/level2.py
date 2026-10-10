import sys


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


def solve(data):
    return "\n".join("%d %d" % simulate(seq) for seq in parse(data)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
