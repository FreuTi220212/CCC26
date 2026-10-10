import sys

BEATS = {"R": "S", "S": "P", "P": "R"}  # Schluessel schlaegt Wert


def winner(a, b):
    if a == b or BEATS[a] == b:
        return a
    return b


def solve(data):
    lines = data.split()
    n = int(lines[0])
    return "\n".join(winner(s[0], s[1]) for s in lines[1:1 + n])


if __name__ == "__main__":
    out = solve(sys.stdin.read())
    sys.stdout.write(out + "\n")
