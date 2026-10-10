import sys

BEATS = {"R": "S", "S": "P", "P": "R"}  # Schluessel schlaegt Wert


def winner(a, b):
    if a == b or BEATS[a] == b:
        return a
    return b


def play_round(styles):
    return [winner(styles[i], styles[i + 1]) for i in range(0, len(styles) - 1, 2)]


def tournament(styles, rounds):
    styles = list(styles)
    for _ in range(rounds):
        if len(styles) < 2:
            break
        styles = play_round(styles)
    return "".join(styles)


def solve(data):
    lines = data.split()
    n = int(lines[0])
    return "\n".join(tournament(s, 2) for s in lines[2:2 + n])


if __name__ == "__main__":
    out = solve(sys.stdin.read())
    sys.stdout.write(out + "\n")
