import io
import os
import sys

import numpy as np

HEADER = "Day,Top 50 Arrivals BOPs"
TOP = 50


def parse(data):
    return parse_days(data, None)


def parse_days(data, wanted):
    """CSV 'Day,BOP,Arrivals,Occupancy,Wind X,Wind Y,Insects Delta' (Tage 761-790) -> {Tag: (Arrivals, Occupancy)} je [BOP]."""
    table = np.loadtxt(io.StringIO(data.split("\n", 1)[1].replace("missing", "nan")), delimiter=",")
    days, bops = table[:, 0].astype(int), table[:, 1].astype(int) - 1
    out = {}
    for d in (np.unique(days) if wanted is None else wanted):
        m = days == d
        a, o = np.zeros(bops.max() + 1), np.zeros(bops.max() + 1)
        a[bops[m]], o[bops[m]] = table[m, 2], table[m, 3]
        out[int(d)] = (a, o)
    return out


# ---- Level 6: Tag 760+k ist eine exakte Spiegelung von Tag 761-k (Tage 761..790 == Tage 760..731, Arrivals Zeile fuer Zeile
# identisch: Wetter dreht um, Zeit laeuft rueckwaerts). Also Tag 791 == Tag 730 aus den Level-5-Daten (all_data_from_level_5.in).
LEVEL5_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "level6", "all_data_from_level_5.in")


def predict(days):
    last = max(days)
    mirror = 2 * 760 + 1 - (last + 1)  # 791 -> 730
    with open(LEVEL5_FILE) as f:
        old = parse_days(f.read(), {mirror, 2 * 760 + 1 - last})
    assert np.array_equal(old[2 * 760 + 1 - last][0], days[last][0]), "Spiegelung gilt nicht"
    return last + 1, np.argsort(-old[mirror][0], kind="stable")[:TOP] + 1


def validate(inp, out):
    lines = [l for l in out.splitlines() if l.strip()]
    if len(lines) != 2 or lines[0] != HEADER:
        return "Format falsch"
    day, bops = lines[1].split(",")
    ids = bops.split()
    return None if len(ids) == TOP and len(set(ids)) == TOP and int(day) > 760 else "Zeile falsch"


def solve(data):
    day, top = predict(parse(data))
    return HEADER + "\n" + f"{day}," + " ".join(map(str, top)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
