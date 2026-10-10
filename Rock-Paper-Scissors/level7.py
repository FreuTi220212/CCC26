import sys

# Stile: R=Rock, P=Paper, S=Scissors, Y=Spock, L=Lizard. Schluessel schlaegt Werte.
BEATS = {"R": "LS", "P": "RY", "S": "PL", "L": "YP", "Y": "SR"}
STYLES = "RPSYL"
IDX = {c: i for i, c in enumerate(STYLES)}
FULL = 31


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


WIN = [[IDX[winner(a, b)] for b in STYLES] for a in STYLES]


def _comb(ma, mb):
    r = 0
    for a in range(5):
        if ma >> a & 1:
            for b in range(5):
                if mb >> b & 1:
                    r |= 1 << WIN[a][b]
    return r


# COMB[ma][mb] = Menge moeglicher Sieger, wenn links ma und rechts mb moeglich sind (Gegner waehlt Z unabhaengig)
COMB = [[_comb(a, b) for b in range(32)] for a in range(32)]


# ---- Level 7: 'Z' = Gegner waehlt beliebig, 'X' = wir waehlen. S muss immer gewinnen.
# Je Knoten: Familie minimaler Sieger-Mengen, die wir durch unsere X-Wahl erzwingen koennen.
# Kleinere Menge ist immer besser (monoton), daher nur minimale behalten.
def minimal(masks):
    masks = sorted(set(masks), key=lambda m: bin(m).count("1"))
    keep = []
    for m in masks:
        if not any(k & m == k for k in keep):
            keep.append(m)
    return keep


def fill(line):
    # Ebene 0: Blaetter; je Knoten dict mask -> (linke mask, rechte mask) bzw. Buchstabe
    level = []
    for c in line:
        if c == "X":
            level.append({1 << i: i for i in range(5)})
        elif c == "Z":
            level.append({FULL: None})
        else:
            level.append({1 << IDX[c]: None})
    levels = [level]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            res = {}
            for ma in level[i]:
                for mb in level[i + 1]:
                    res.setdefault(COMB[ma][mb], (ma, mb))
            keep = minimal(res)
            nxt.append({m: res[m] for m in keep})
        levels.append(nxt)
        level = nxt
    root = level[0]
    target = 1 << IDX["S"]
    if target not in root:
        raise ValueError("keine Loesung")
    masks = [target]
    for lvl in range(len(levels) - 1, 0, -1):
        nxt = []
        for i, m in enumerate(masks):
            ma, mb = levels[lvl][i][m]
            nxt += [ma, mb]
        masks = nxt
    out = []
    for c, m in zip(line, masks):
        out.append(STYLES[levels[0][len(out)][m]] if c == "X" else c)
    return "".join(out)


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
            return f"Zeile {i + 1}: feste Plaetze/Z veraendert"
        if "X" in line:
            return f"Zeile {i + 1}: X nicht ersetzt"
        cur = [FULL if c == "Z" else 1 << IDX[c] for c in line]
        while len(cur) > 1:
            cur = [COMB[cur[j]][cur[j + 1]] for j in range(0, len(cur), 2)]
        if cur[0] != 1 << IDX["S"]:
            return f"Zeile {i + 1}: moegliche Sieger {cur[0]:05b}"
    return None


def solve(data):
    t = data.split()
    n = int(t[0])
    return "\n".join(fill(t[2 + i]) for i in range(n))


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
