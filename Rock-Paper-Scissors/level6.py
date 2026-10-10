import sys

# Stile: R=Rock, P=Paper, S=Scissors, Y=Spock, L=Lizard. Schluessel schlaegt Werte.
BEATS = {"R": "LS", "P": "RY", "S": "PL", "L": "YP", "Y": "SR"}
STYLES = "RPSYL"
IDX = {c: i for i, c in enumerate(STYLES)}


def winner(a, b):
    if a == b or b in BEATS[a]:
        return a
    return b


def play_round(styles):
    return [winner(styles[i], styles[i + 1]) for i in range(0, len(styles) - 1, 2)]


def tournament(styles, rounds=99):
    styles = list(styles)
    for _ in range(rounds):
        if len(styles) < 2:
            break
        styles = play_round(styles)
    return "".join(styles)


# ---- Level 6: 'X' = freie Plaetze, so belegen dass S gewinnt.
# Bottom-up: je Knoten Bitmaske der moeglichen Sieger; top-down: Ziel S, Kinderziele passend waehlen.
WIN = [[IDX[winner(a, b)] for b in STYLES] for a in STYLES]
COMBINE = {}  # (maskA, maskB) -> mask


def combine(ma, mb):
    key = (ma, mb)
    r = COMBINE.get(key)
    if r is None:
        r = 0
        for a in range(5):
            if ma >> a & 1:
                for b in range(5):
                    if mb >> b & 1:
                        r |= 1 << WIN[a][b]
        COMBINE[key] = r
    return r


def fill(line, target="S"):
    leaves = [31 if c == "X" else 1 << IDX[c] for c in line]
    levels = [leaves]
    while len(levels[-1]) > 1:
        cur = levels[-1]
        levels.append([combine(cur[i], cur[i + 1]) for i in range(0, len(cur), 2)])
    t = IDX[target]
    if not levels[-1][0] >> t & 1:
        raise ValueError("keine Loesung")
    targets = [t]
    for lvl in range(len(levels) - 2, -1, -1):
        cur = levels[lvl]
        nxt = []
        for i, tg in enumerate(targets):
            ma, mb = cur[2 * i], cur[2 * i + 1]
            for a in range(5):
                if ma >> a & 1:
                    b = next((b for b in range(5) if mb >> b & 1 and WIN[a][b] == tg), None)
                    if b is not None:
                        nxt += [a, b]
                        break
        targets = nxt
    return "".join(STYLES[x] for x in targets)


def validate(inp, out):
    """None wenn ok, sonst Fehlertext."""
    t = inp.split()
    n, m = int(t[0]), int(t[1])
    res = out.split()
    if len(res) != n:
        return f"{len(res)} Zeilen statt {n}"
    for i, line in enumerate(res):
        src = t[2 + i]
        if len(line) != m or any(a != "X" and a != b for a, b in zip(src, line)):
            return f"Zeile {i + 1}: feste Plaetze veraendert"
        if tournament(line) != "S":
            return f"Zeile {i + 1}: Sieger {tournament(line)!r}"
    return None


def solve(data):
    t = data.split()
    n = int(t[0])
    return "\n".join(fill(t[2 + i]) for i in range(n))


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
