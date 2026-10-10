import io
import sys

import numpy as np

HEADER = "Day,Top 50 Arrivals BOPs"
FIRST_FORECAST_DAY, LAST_FORECAST_DAY, TOP = 731, 760, 50


def parse(data):
    """CSV 'Day,BOP,Arrivals,Occupancy,Wind X,Wind Y,Insects Delta' (58 MB) -> Arrays [Tag, BOP] fuer Arrivals/Occupancy."""
    body = data.split("\n", 1)[1].replace("missing", "nan")
    table = np.loadtxt(io.StringIO(body), delimiter=",")  # C-Parser: 1,6 s statt 68 s (np.fromstring) / 13 s (genfromtxt)
    days, bops = table[:, 0].astype(int), table[:, 1].astype(int)
    arrivals = np.full((days.max() + 1, bops.max() + 1), np.nan)
    occupancy = arrivals.copy()
    arrivals[days, bops] = table[:, 2]
    occupancy[days, bops] = table[:, 3]
    return arrivals[1:, 1:], occupancy[1:, 1:]


# ---- Level 5: Top-50-BOPs nach Arrivals fuer Tag 731..760. Ergebnis der Plattform-Tests (Rueckblicktests auf den Trainingstagen
# taeuschten): Occupancy des Prognosetages allein BESTEHT; Occupancy*Verhaeltnis (Gesamtmittel) 0.496, Rangsumme mit
# Verhaeltnis der letzten 30/60 Tage 0.4287. Das Verhaeltnis Arrivals/Occupancy driftet, die Belegung der Prognosetage
# (Korrelation ~0.87 mit Arrivals) ist der stabile Anker. Wetter, Pfad-Graph (Level 4), Vorjahr, Regression halfen nicht.
def forecast(arrivals, occupancy):
    lines = []
    for day in range(FIRST_FORECAST_DAY, LAST_FORECAST_DAY + 1):
        top = np.argsort(-occupancy[day - 1], kind="stable")[:TOP] + 1
        lines.append(f"{day}," + " ".join(map(str, top)))
    return lines


def validate(inp, out):
    """Nur Format: Kopfzeile, 30 Tage, je 50 verschiedene BOP-Nummern."""
    lines = [l for l in out.splitlines() if l.strip()]
    if not lines or lines[0] != HEADER:
        return "Kopfzeile falsch"
    if len(lines) != 1 + LAST_FORECAST_DAY - FIRST_FORECAST_DAY + 1:
        return f"{len(lines) - 1} Tage statt 30"
    for day, line in zip(range(FIRST_FORECAST_DAY, LAST_FORECAST_DAY + 1), lines[1:]):
        d, bops = line.split(",")
        ids = bops.split()
        if int(d) != day or len(ids) != TOP or len(set(ids)) != TOP:
            return f"Tag {day}: falsch"
    return None


def solve(data):
    arrivals, occupancy = parse(data)
    return HEADER + "\n" + "\n".join(forecast(arrivals, occupancy)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
