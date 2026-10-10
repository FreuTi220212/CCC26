# Classic-Spaceship (CCC 2025.11 Classic, Level 1-8, abgeschlossen)

Allgemeine Regeln: ../CLAUDE.md. Hier nur Spielregeln, Input je Level, Fehler/Zeitfresser. Pro Level: Beispiel + small + large.

## Regeln und Input-Struktur
- Raumschiff in 1D/2D, Achsen unabhängig. Pace p>0: +1 Weg in Zeit p; p<0: -1 Weg in |p|; 0: kein Weg, Zeit 1.
- Pace-Folge beginnt und endet mit 0; Pace darf nur zu einem Nachbarn (oder gleich) wechseln in der Reihenfolge `-1 -2 -3 -4 -5 0 5 4 3 2 1`.
- **Zeitkonvention (per Plattformtest bestätigt): die Position ändert sich erst am ENDE der Pace-Dauer.** Gilt auch für Asteroiden (L8).
- Kollision = Chebyshev-Abstand <= 2 zwischen Schiff und Asteroid (5x5-Quadrat; steht nur als Bild auf PDF-Seite 3 von L5).
- L1: Summe der Paces je Zeile. L2: `Endposition Zeit`, Paces auch 0/negativ.
- L3: `Position Limit` -> Folge mit exakter Position und Zeit <= Limit (Limit großzügig; Rampe 5,4,..,peak, Reise, zurück; PDF-Text teils verschlüsselt).
- L4: 2D, `x,y limit` -> X-Folge und Y-Folge, beide <= Limit = Optimum je Achse: Dijkstra über (Position, Pace). Ziel 0 -> Folge `0`.
- L5: 1 ruhender Asteroid (`ax,ay`). Achsen nacheinander fahren (andere wartet mit Nullen), L-Weg, sonst Gitter-Dijkstra.
- L6: Limit knapp: Achsen parallel, Startverzögerung, Abstecher, Wegpunkte.
- L7: viele Asteroiden (5000, ~20 % gesperrt, labyrinthartig), Limit knapp. `Planner.java`: gewichtetes A* im vollen Zustand (x, y, Pace-Zustand X/Y), BFS-Zugzahl-Heuristik.
- L8: Asteroiden bewegen sich (`ax,ay,px,py`, Pace je Achse, 0 = steht): Position zum Tick t = x0 + vorzeichen * ((t+1) // |pace|). `Planner8.java`: Zeit im Schlüssel, Sperrkarte je Tick.
- Ausgabe je Fall: X-Zeile, Y-Zeile, Leerzeile.

## Fehler und Zeitfresser (Reihenfolge nach verlorener Zeit)
1. L7: ~3 h in Python (starre Hauptachse, Beam, Segmente + A*, Zeit-DP: 18/20 small). Danach Java-A* in 1 h: 20/20 + large. -> Zustandsraumsuche von Anfang an in Java.
2. L7: BFS-Heuristik mit Eckenprüfung war unzulässig (schnitt Lösungen weg). Bei Rechenabbruch größere Gewichte probieren (1.5 -> 2.5 -> 4).
3. L7: Strenge "Sprung am Anfang"-Validierung scheiterte am Limit; Ein Plattform-Upload der Variante "Sprung am Ende" klärte es (20/20).
4. L8: Konvention der bewegten Asteroiden an den Beispiel-Lösungen aller Varianten durchprobiert: nur Schiff-Ende + Asteroid-Ende war kollisionsfrei. 1 Versuch.
5. L6: sequentielle L5-Lösung zu langsam; paralleler Flug mit Verzögerung/Abstecher/Wegpunkten.
6. Wiederholt: `\n` per Bash-Heredoc (SyntaxError), unzulässige Heuristik, Tuple-Vorrang (`return a, b if c else None`).
7. Explorer wurde einmal doppelt geöffnet (Befehl zweimal ausgeführt). `open_output.ps1` prüft das jetzt.
