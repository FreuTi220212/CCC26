import sys


def parse(data):
    """N, dann N Zeilen mit Pace-Werten (Zeit pro Streckeneinheit)."""
    lines = data.splitlines()
    n = int(lines[0])
    return [[int(x) for x in line.split()] for line in lines[1:1 + n]]


def total_time(paces):
    """Jede Pace p braucht p Zeiteinheiten fuer 1 Streckeneinheit."""
    return sum(paces)


def solve(data):
    return "\n".join(str(total_time(seq)) for seq in parse(data)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
