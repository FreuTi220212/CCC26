import collections
import sys

import numpy as np

from level2 import level1_table  # Temperaturen je BOP (Fahrenheit-Fehler korrigiert)

HEADER = "Flock ID,Species"
SEG_T, BO_T, DIFF_T, A2_T = 0.15, 0.2, 0.15, 0.45  # Schwellen, an den 288 gelabelten Schwaermen abgestimmt (284 richtig)


def parse(data):
    """CSV 'Flock ID,BOP Path,Species' -> (Reihenfolge der Schwaerme, {flock: [Pfade]}, {flock: Art oder None})."""
    order, paths, species = [], collections.defaultdict(list), {}
    for line in data.splitlines()[1:]:
        if not line.strip():
            continue
        fid, rest = line.split(",", 1)
        path, sp = rest.rsplit(",", 1)
        f = int(fid)
        if f not in species:
            order.append(f)
        paths[f].append([int(b) for b in path.split()])
        species[f] = None if sp.strip() == "missing" else sp.strip()
    return order, dict(paths), species


def agreement(paths):
    """Mittlere Uebereinstimmung der Voegel je Position (erste / zweite Pfadhaelfte, ohne Start/Ende)."""
    length, n, ag = min(len(p) for p in paths), len(paths), []
    for j in range(1, length - 1):
        ag.append(collections.Counter(p[j] for p in paths).most_common(1)[0][1] / n)
    ag = np.array(ag)
    h = len(ag) // 2
    return (ag[:h].mean() if h else 1.0), (ag[h:].mean() if len(ag) > h else 1.0)


def dup_fraction(paths):
    """Anteil wiederholter Knoten im Pfad: ~0.45 bei Hin-und-zurueck-Routen (Bluetit), sonst ~0."""
    return float(np.mean([(len(p) - 1 - len(set(p))) / (len(p) - 1) for p in paths]))


# ---- Level 4: Art je Schwarm aus Merkmalen (Entscheidungsliste, an Level 3 / den bekannten Schwaermen abgeleitet)
#  Red Firefinch: viele Voegel (>= 7) oder kurze, voellig verschiedene Pfade | Hurracurra: heisse BOPs (Temp ~43.6)
#  Medieval Bluetit: Hin = Rueckweg (viele wiederholte Knoten) | Sticky Wolfthroat: kurzer Pfad oder Segmente der
#  Bluetit-Routen | Flanking Blackfinch: ganze Strecke gemeinsam | Rusty Goldhammer: erste Haelfte gemeinsam, zweite verschieden
def classify_all(paths, temps):
    blue = [f for f, p in paths.items() if dup_fraction(p) >= 0.3]  # alle bluetit-artigen Schwaerme (auch ungelabelte)
    routes = {f: {b for p in paths[f] for b in p} for f in blue}
    pairs = {frozenset((p[i], p[i + 1])) for f in blue for p in paths[f] for i in range(len(p) - 1)}
    res = {}
    for f, ps in paths.items():
        n, length = len(ps), min(len(p) for p in ps)
        a1, a2 = agreement(ps)
        nodes = {b for p in ps for b in p}
        total = sum(len(p) - 1 for p in ps)
        seg = sum(frozenset((p[i], p[i + 1])) in pairs for p in ps for i in range(len(p) - 1)) / total
        bo1 = max((len(nodes & r) / len(nodes) for g, r in routes.items() if g != f), default=0.0)
        if np.mean([temps[b] for p in ps for b in p]) > 40:
            res[f] = "Hurracurra Bird"
        elif n >= 7 or (a1 < 0.19 and a2 < 0.19 and length <= 19) or (n < 3 and a1 <= 1 / n + 0.01 and a2 <= 1 / n + 0.01):
            res[f] = "Red Firefinch"
        elif dup_fraction(ps) >= 0.3:
            res[f] = "Medieval Bluetit"
        elif seg >= SEG_T or length <= 10 or (length == 11 and bo1 >= BO_T):
            res[f] = "Sticky Wolfthroat"
        elif a2 >= A2_T:
            res[f] = "Flanking Blackfinch"
        else:
            res[f] = "Rusty Goldhammer" if a1 - a2 >= DIFF_T else "Flanking Blackfinch"
    return res


def solve(data):
    order, paths, species = parse(data)
    pred = classify_all(paths, {b: t for b, (t, h) in level1_table().items()})
    return HEADER + "\n" + "\n".join(f"{f},{pred[f]}" for f in order if species[f] is None)  # Beispiel-Output ohne Zeilenumbruch am Ende


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
