import glob
import os
import sys

import numpy as np

from level1 import parse as parse_level1  # Level-1-Daten wiederverwenden (Temperatur, Luftfeuchte je BOP)

HERE = os.path.dirname(os.path.abspath(__file__))
HEADER = "BOP,Bird Love Score [<3]"
F_THRESHOLD = 55  # Level-1-Temperaturen > 55 sind versehentlich in Fahrenheit (die Werte 50-69 kommen nicht vor)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def level1_table():
    """BOP -> (Temperatur in Grad C, Luftfeuchte) aus allen Level-1-Dateien (Beispiel ausgenommen)."""
    tab = {}
    for f in sorted(glob.glob(os.path.join(HERE, "level1", "in_level-1_[1-9]*.txt"))):
        for bop, temp, hum in parse_level1(read(f)):
            tab.setdefault(bop, (temp, hum))
    return {b: ((t - 32) * 5 / 9 if t > F_THRESHOLD else float(t), float(h)) for b, (t, h) in tab.items()}


def parse(data):
    """CSV mit Kopfzeile: BOP, Vegetation, Insekten, Stadtlicht, Score ('missing' = unbekannt)."""
    rows = []
    for line in data.splitlines()[1:]:
        if line.strip():
            p = [v.strip() for v in line.split(",")]
            rows.append((int(p[0]), float(p[1]), float(p[2]), float(p[3]), None if p[4] == "missing" else float(p[4])))
    return rows


def features(rows, tab):
    return np.array([[1.0, tab[b][0], tab[b][1], ins, urb, veg] for b, veg, ins, urb, _ in rows])


def training_data(tab):
    """Alle bekannten Scores aus allen Level-2-Dateien (c hat keine eigenen Scores)."""
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, "level2", "in_level-2_[1-9]*.txt"))):
        rows += [r for r in parse(read(f)) if r[4] is not None and r[0] > 5]
    return features(rows, tab), np.array([r[4] for r in rows])


def predict_missing(data):
    tab = level1_table()
    x, y = training_data(tab)
    w, *_ = np.linalg.lstsq(x, y, rcond=None)  # CV-RMSE ~2.6: Score ~ 1.7 * Temperatur, Rest ist Rauschen
    todo = [r for r in parse(data) if r[4] is None]
    pred = features(todo, tab) @ w
    return [(r[0], p) for r, p in zip(todo, pred)]


def validate(inp, out):
    """Nur Format: Kopfzeile, genau die fehlenden BOPs in Eingabereihenfolge, Zahlen mit 2 Nachkommastellen."""
    missing = [r[0] for r in parse(inp) if r[4] is None]
    lines = [l for l in out.splitlines() if l.strip()]
    if not lines or lines[0] != HEADER:
        return "Kopfzeile falsch"
    if len(lines) - 1 != len(missing):
        return f"{len(lines) - 1} Zeilen statt {len(missing)}"
    for bop, line in zip(missing, lines[1:]):
        p = line.split(",")
        if len(p) != 2 or int(p[0]) != bop or len(p[1].split(".")[-1]) != 2:
            return f"Zeile fuer BOP {bop} falsch: {line!r}"
        float(p[1])
    return None


def solve(data):
    return HEADER + "\n" + "\n".join(f"{bop},{p:.2f}" for bop, p in predict_missing(data)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
