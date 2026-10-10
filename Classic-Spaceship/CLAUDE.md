# Classic-Spaceship (CCC 2025.11 Classic, in Arbeit)

Allgemeine Regeln: ../CLAUDE.md. Hier nur Spielregeln, Input-Struktur je Level und Log.

## Regeln und Input-Struktur
- Raumschiff, eindimensional. Pace = Zeit pro Streckeneinheit: `p>0` -> +1 Weg in Zeit p, `p<0` -> -1 Weg in Zeit |p|, `0` -> kein Weg, 1 Zeit.
- Level 1: `N`, N Zeilen mit positiven Paces -> Gesamtzeit (Summe) je Zeile.
- Level 2: Paces auch 0 und negativ -> `Endposition Zeit` je Zeile (Start bei 0).
- Level 3: `N`, je Zeile `Position Zeitlimit` -> Pace-Folge, die Position exakt erreicht, Zeit <= Limit. Folge beginnt und endet mit 0,
  Paces nur schrittweise änderbar in der Reihenfolge -1 -2 -3 -4 -5 0 5 4 3 2 1 (Nachbarn oder gleich). Mehrere Lösungen -> `validate`.
  Lösung: 0, Rampe 5,4,..,peak, Reise mit peak, Rampe zurück, 0 (peak 1..5, schnellste Variante); Vorzeichen für negative Ziele.

## Log
- L1, L2, L3: je 1 Versuch, Laufzeiten < 0,2 s. PDF-Text bei L3 teilweise verschlüsselt ("Zeitlimit ist großzügig") -> Bild lesen/Limits prüfen.
