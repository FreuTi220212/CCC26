import collections
import sys

from level2 import level1_table  # Temperaturen je BOP (Fahrenheit-Fehler korrigiert)

HEADER = "Flock ID,Species"


def parse(data):
    """CSV: 'Flock ID,BOP Path' -> {flock: [Pfad je Vogel]}; Pfad = Liste von BOP-Nummern."""
    flocks = collections.defaultdict(list)
    for line in data.splitlines()[1:]:
        if line.strip():
            fid, path = line.split(",", 1)
            flocks[int(fid)].append([int(b) for b in path.split()])
    return dict(flocks)


# ---- Level 3: Schwarm -> Art. Merkmale (an a/b/c verifiziert, je Datei genau ein Schwarm pro Art):
#  Medieval Bluetit    : alle Voegel identisch, Pfad palindromisch (Rueckweg = Hinweg); von den (zwei) solchen Schwaerten
#                        der mit den MEISTEN verschiedenen BOPs (lange Route; Beispiel-Loesung: Bluetit = lange Route 1..7..1)
#  Sticky Wolfthroat   : der Schwarm, dessen BOPs (fast) alle auf der Bluetit-Route liegen (lauert an Routenabschnitten)
#  Flanking Blackfinch : alle Voegel identisch, geschlossene Schleife, nicht palindromisch (umkreist ein Gebiet gemeinsam)
#  Hurracurra Bird     : unter den uebrigen die hoechste mittlere Temperatur der besuchten BOPs (heisse Regionen)
#  Rusty Goldhammer    : langes gemeinsames Praefix (zusammen hin, getrennt zurueck)
#  Red Firefinch       : der Rest (gemeinsam nur das Nest am Anfang/Ende, sonst eigene Ausfluege)
def features(paths):
    ident = len({tuple(p) for p in paths}) == 1
    pal = all(p == p[::-1] for p in paths)
    n = min(len(p) for p in paths)
    pre = 0
    while pre < n and len({p[pre] for p in paths}) == 1:
        pre += 1
    nodes = {b for p in paths for b in p}
    return {"ident": ident, "pal": pal, "pre": pre / n, "nodes": nodes, "closed": all(p[0] == p[-1] for p in paths)}


def classify(flocks, temps):
    feat = {f: features(p) for f, p in flocks.items()}
    left, res = set(flocks), {}

    def take(fid, species):
        res[fid] = species
        left.discard(fid)

    pal_ident = [f for f in left if feat[f]["ident"] and feat[f]["pal"]]
    if pal_ident:
        blue = max(pal_ident, key=lambda f: len(feat[f]["nodes"]))  # Bluetit = laengere Route, der Wolfthroat lauert an deren Abschnitten
        take(blue, "Medieval Bluetit")
        cands = [f for f in left if feat[f]["nodes"] & feat[blue]["nodes"]]
        if cands:
            take(max(cands, key=lambda f: (len(feat[f]["nodes"] & feat[blue]["nodes"]) / len(feat[f]["nodes"]), feat[f]["pal"])),
                 "Sticky Wolfthroat")  # Anteil der EIGENEN Knoten auf der Bluetit-Route
    black = [f for f in left if feat[f]["ident"] and feat[f]["closed"] and not feat[f]["pal"]]
    if black:
        take(black[0], "Flanking Blackfinch")
    rest = [f for f in left if not feat[f]["ident"]]
    if rest:
        hot = max(rest, key=lambda f: sum(temps[b] for p in flocks[f] for b in p) / sum(len(p) for p in flocks[f]))
        take(hot, "Hurracurra Bird")
        rest = [f for f in rest if f != hot]
    if rest:
        gold = max(rest, key=lambda f: feat[f]["pre"])
        take(gold, "Rusty Goldhammer")
        rest = [f for f in rest if f != gold]
    if rest:
        take(rest[0], "Red Firefinch")
    return res


def solve(data):
    flocks = parse(data)
    res = classify(flocks, {b: t for b, (t, h) in level1_table().items()})
    return HEADER + "\n" + "\n".join(f"{f},{res.get(f, '?')}" for f in sorted(flocks)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
