import sys

WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen".split())}
WORDS.update({w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())})


def to_int(token):
    """Zahl als Ziffern oder englisches Zahlwort ('seventeen', 'twenty-one', 'minus five')."""
    t = token.strip().lower()
    try:
        return int(t)
    except ValueError:
        pass
    sign, total = 1, 0
    for w in t.replace("-", " ").split():
        if w in ("minus", "negative"):
            sign = -1
        elif w == "hundred":
            total = max(total, 1) * 100
        elif w in WORDS:
            total += WORDS[w]
        elif w != "and":
            raise ValueError(f"unbekannte Zahl: {token!r}")
    return sign * total


def parse(data):
    """CSV: Kopfzeile, dann 'BOP,Temperatur,Luftfeuchte' je Zeile (Zahlen teils als Wort geschrieben)."""
    rows = []
    for line in data.splitlines()[1:]:
        if line.strip():
            bop, temp, hum = (to_int(v) for v in line.split(","))
            rows.append((bop, temp, hum))
    return rows


def popularity_order(rows):
    """Vogel mag es warm, bei gleicher Temperatur trocken; Gleichstand: kleinere BOP-Nr. zuerst."""
    return [bop for bop, temp, hum in sorted(rows, key=lambda r: (-r[1], r[2], r[0]))]


def solve(data):
    return " ".join(map(str, popularity_order(parse(data))))  # Beispiel-Output hat KEINEN Zeilenumbruch am Ende


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
