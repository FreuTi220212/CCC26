# Rock-Paper-Scissors (Training, Level 1-7, abgeschlossen)

Allgemeine Regeln stehen in `../CLAUDE.md`. Hier nur Spielspezifisches.

## Regeln und Input-Struktur
- Single-Elimination, Paare (0,1),(2,3)…, M Zweierpotenz. R>S, S>P, P>R, gleicher Stil -> gleicher Stil gewinnt.
- Ab Level 5 fünf Stile, Input-Reihenfolge `R P S Y(Spock) L(Lizard)`: R>L,S; P>R,Y; S>P,L; L>Y,P; Y>S,R.
- Level 1: `N`, N Zeilen mit 2 Zeichen -> Gewinnerstil je Zeile.
- Level 2: `N M`, N Strings (Länge M) -> Überlebende nach 2 Runden, Reihenfolge erhalten.
- Level 3: `N M`, N Zeilen `aR bP cS` -> Aufstellung (Länge M), nach 2 Runden kein R, >=1 S. 4er-Blöcke, jeder Block mit R braucht ein P, ein Block gezielt für S.
- Level 4: wie 3, Sieger nach ALLEN Runden S. Kette `S` + Teilbäume der Größe 1,2,4,…; R nur in Teilbäumen mit >=1 P; S-Füller als Paar `RS`.
- Level 5: 5 Stile, Sieger S. Rückwärts-Verdopplung (Start [S], pro Schritt bekommt jeder einen Gegner, den er schlägt/gleich), exakt per ILP (`scipy.optimize.milp`).
- Level 6: feste Kämpfer plus `X` (frei wählbar), Sieger S. DP: Bitmaske möglicher Sieger je Knoten, top-down Ziele verteilen.
- Level 7: zusätzlich `Z` (Gegner wählt beliebig), S muss immer gewinnen, `Z` bleibt im Output. Familie minimaler Sieger-Mengen je Knoten.

## Log (je 1 Versuch bis Beispiel/`validate` OK, außer genannt)
- L1: Upload zuerst falsch (`level1.py` statt Outputs hochgeladen). PDF-Seiten waren Bilder (`pdftotext` zeigte nur das I/O-Format).
- L3-L7: Beispiel-Output nicht reproduzierbar (mehrere Lösungen) -> `validate` nachträglich, `run.py` erweitert.
- L4: erste Formel zu streng (nur reine R/P-Teilbäume), per Brute-Force für n<=32 korrigiert.
- L5: Greedy/Zufall/Backtracking scheiterte bei engen Fällen (z. B. 20R 1P 1S 6Y 4L, M=32), viel Zeit verloren; ILP löste alles sofort. Hinweis darauf: exakte Anzahlen + Konstruktion.
- Laufzeiten alle < 8 s (L5 mit ILP am längsten).
- Fehler: `\n` im Bash-Heredoc zerstörte Python-Quelltext (SyntaxError); `/tmp` in bash != Python.
