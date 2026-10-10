# Classic-Spaceship (CCC 2025.11 Classic, in Arbeit)

Allgemeine Regeln: ../CLAUDE.md. Hier nur Spielregeln, Input-Struktur je Level und Log.

## Regeln und Input-Struktur
- Raumschiff, eindimensional. Pace = Zeit pro Streckeneinheit: `p>0` -> +1 Weg in Zeit p, `p<0` -> -1 Weg in Zeit |p|, `0` -> kein Weg, 1 Zeit.
- Level 1: `N`, N Zeilen mit positiven Paces -> Gesamtzeit (Summe) je Zeile.
- Level 2: Paces auch 0 und negativ -> `Endposition Zeit` je Zeile (Start bei 0).
- Level 3: `N`, je Zeile `Position Zeitlimit` -> Pace-Folge, die Position exakt erreicht, Zeit <= Limit. Folge beginnt und endet mit 0,
  Paces nur schrittweise änderbar in der Reihenfolge -1 -2 -3 -4 -5 0 5 4 3 2 1 (Nachbarn oder gleich). Mehrere Lösungen -> `validate`.
  Lösung: 0, Rampe 5,4,..,peak, Reise mit peak, Rampe zurück, 0 (peak 1..5, schnellste Variante); Vorzeichen für negative Ziele.
- Level 4: 2D, `N`, je Zeile `x,y limit` -> je Fall zwei Folgen (X, dann Y), Leerzeile zwischen Fällen empfohlen. Beide Folgen innerhalb Limit = Optimum je Achse. Dijkstra über (Position, Pace) mit Nachbarschaft wie in Level 3; Ziel 0 -> Folge `0`. Validator prüft Pace-Wechsel, Position, Zeit.
- Level 5: je Fall `x,y limit` + Zeile `ax,ay` (1 ruhender Asteroid). Kollision = Chebyshev-Abstand Schiff-Asteroid <= 2 (5x5-Quadrat, auf PDF-Seite 3 als Bild). Beide Achsenfolgen laufen parallel in der Zeit; Lösung fährt Achsen nacheinander (die andere wartet mit Nullen gleicher Dauer), Weg erst als L-Weg, bei Blockade Dijkstra auf dem Gitter mit Abbiege-Strafe. Segmente mit der Level-4-Optimalfolge. Validator prüft Kollision für Sprung am Pace-Anfang UND -Ende.

## Log
- L1, L2, L3: je 1 Versuch, Laufzeiten < 0,2 s. PDF-Text bei L3 teilweise verschlüsselt ("Zeitlimit ist großzügig") -> Bild lesen/Limits prüfen.
- L4: 1 Versuch. Limit entspricht exakt dem Optimum (Dijkstra), Level-3-Rampenfamilie hätte vermutlich auch gereicht.
- L5: Dijkstra pro Fall war bei N=1000 zu langsam (>60 s) -> erst L-Wege prüfen, nur bei Blockade Gitter-Dijkstra (0,35 s). Hinweis: Regeln zu Kollision standen nur im Bild.
