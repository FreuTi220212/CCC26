# CCC (Cloudflight Coding Contest) - Python + Java, Windows

Ein Ordner pro Spiel (`Rock-Paper-Scissors/`, `School-Magic-Money/`, `Asteroid-Mining/`, `Classic-Spaceship/`), Werkzeuge in `_template/`.
Jedes Spiel hat eine eigene `CLAUDE.md` (Regeln, Input-Struktur, Fehler). Bei Problemen dort nach ähnlichen Fällen suchen.

## Prioritäten (in dieser Reihenfolge)
1. Teilaufgaben (Level) präzise und SCHNELL lösen. Während eines Projekts weder dokumentieren noch committen.
2. Erst NACH dem letzten Level: Spiel-`CLAUDE.md` schreiben (Regeln, Input je Level, Fehler/Zeitfresser), neue allgemeine Regeln hier ergänzen, EIN Commit.
3. Antworten an den Nutzer minimal: pro Level 1 Zeile ("Level N fertig, Explorer offen") oder der Blocker. Keine Lösungsbeschreibung, Laufzeit oder Doku-Hinweise. Nur bei echter Blockade fragen.
4. Explorer nur ÖFFNEN (`open_output.ps1 N`, öffnet nie doppelt), nie schließen: der Nutzer schließt selbst.
5. Erst small 100 % grün, dann large (`run.py` überspringt large nach einem small-Fehler). Zeit nicht an large verschwenden.

## Ablauf pro Level
0. Neues Spiel: `powershell -File _template\new_game.ps1 <Name>`, `cd <Name>`, Monitor-Tool mit `powershell -NoProfile -File <Name>/watch_zips.ps1` (timeout 30 min, bei Ablauf SOFORT neu starten). Läuft durchgehend bis Spielende, meldet jede neue .zip als Pfad.
1. Zip gemeldet: `python run.py go "<Pfad>"` (Level-Nr. aus dem Zip, entpackt flach, rendert PDF -> `levelN/pages/p*.png`, zeigt Input-Größen, legt `levelN.py` an = Kopie des vorigen Levels).
2. Seiten 2.. ansehen (Regeln, Format, Beispiele stehen oft NUR im Bild, `pdftotext` ist unvollständig/teils verschlüsselt). Nicht auf Antwort warten.
3. Input-Größen/Limits ansehen (`go` zeigt sie), Algorithmus passend wählen (Tabelle unten).
4. `levelN.py` erweitern (nicht neu schreiben), `solve(data)` rein. Mehrere gültige Lösungen/Limit/"Optimum"? ZUERST `validate(inp, out)` schreiben.
5. `python run.py N` nach jeder Änderung. Fertig = Beispiel + small + large OK, nichts "LANGSAM" (>10 s).
6. `powershell -File open_output.ps1 N`, dann auf das nächste Zip warten. Der Nutzer zieht die `out_*.txt` auf die Seite.

## Aufgabentyp -> was funktioniert hat
- Simulation/Summen/Tabellen: direkt. Große Beträge (1e9): größte Münze in Kopien, Rest per kleiner DP-Tabelle (Tausch-Argument).
- "Generate…"/mehrere Lösungen: Validator per Simulation, nie exakter Vergleich.
- Limit = Optimum (+1): die small-Limits zeigen die Zielgüte. Kleine Fälle per Brute-Force oder `scipy.optimize.milp` (ILP + Fluss-Konnektivität) exakt lösen, Struktur ablesen (Asteroid-Mining L5), dann DP/Formel.
- Konstruktion mit exakten Anzahlen: ILP/DP, NIE Greedy/Zufall (RPS L5 kostete Stunden). Turnier/Baum: rückwärts denken, Bitmasken-DP.
- Zeit-/Kinematikplanung (Classic-Spaceship L4-8): Dijkstra über (Position, Zustand) pro Achse; mit Hindernissen gewichtetes A* im vollen Zustand IN JAVA (`Planner*.java`, JDK 21): Gewichte 1.5 -> 2.5 -> 4, dann 1.25/1.0; Heuristik = BFS-Zugzahl (zulässig: Diagonale ohne Eckenprüfung); Zustände mit g+h > Limit verwerfen; bei Rechenabbruch GRÖSSERES Gewicht. Bewegte Hindernisse: Zeit in den Schlüssel, Sperrkarte je Tick.
- Python-DP/Beam/Segmente für >1e6 Zustände ist verlorene Zeit (Level 7: ~3 h Python, 1 h Java). Nach 20 min ohne tragfähigen Ansatz in Python: Java.

## Plattform-Fakten
- Dateien `in_level-N_X-name.txt` / `out_level-N_X-name.txt`, je Level Beispiel (`_0-example`) + small + large; `level-N.pdf` (Folien), manchmal `sandbox-level-N.html`.
- Output exakt wie im Beispiel-Output (Leerzeile am Ende: `od -c`). Keine Output-Zips. Level gilt erst bei ALLEN Fällen einer Datei als bestanden.
- Das Spiel steckt in einem Cross-Origin-iFrame: Upload nur durch den Nutzer. Browser: Brave. Nie selbst einloggen; Download-Klick nur auf ausdrückliche Bitte. Start: Cookie-Dialog ablehnen, "How to Play" nach unten scrollen -> Close.
- Zips heißen oft `level-N (2).zip`; gleiche Dateien wie ein früheres Level = Kopie (Spiel wurde neu durchgespielt).
- Unklare Konvention (Zeit, Sprung, Kollision)? An den Beispiel-Lösungen des PDFs alle Varianten durchprobieren; sonst Variante hochladen lassen. Die Plattform meldet pro Fall (Screenshot des ersten Fehlfalls) was falsch war.

## Fallen (jeweils real passiert)
- Python-Quelltext nie per Bash-Heredoc/`python -` schreiben (`\n` wird zerstört -> SyntaxError), nur Write/Edit. Auch Java-Strings.
- Bash-`/tmp` != Python-`/tmp`; Temp-Dateien in den Scratchpad. Hintergrundläufe mit Ausgabe puffern: Datei bleibt leer bis Ende.
- Alte Hintergrundprozesse (Python/Java) belegen CPU: vor Messungen mit `Get-CimInstance Win32_Process` prüfen und beenden.
- `return a, b if c else None` ist ein Tupel (Operator-Vorrang). Explorer nur per PowerShell. Zwei Wächter = doppelte Events.
- Gewichtetes A* mit unzulässiger Heuristik schneidet gültige Lösungen weg (Level 7: 677 statt 441).
- Validator nicht strenger als die Plattform bauen: er verwarf Lösungen, die die Plattform akzeptierte.

## Tools (`_template/`, spielunabhängig)
`run.py` (`go [zip]`, `setup N zip`, `info N`, `N [--timeout S --slow S --zip --loose --no-validate --all]`; exakt oder `validate`; small vor large), `level_template.py`, `open_output.ps1`, `watch_zips.ps1`, `new_game.ps1`. Abhängigkeiten: `pip install pymupdf scipy` (installiert), JDK 21 (`javac`/`java`).
Verbesserungen in `_template` UND im aktiven Spiel pflegen.
