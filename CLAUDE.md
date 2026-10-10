# CCC (Cloudflight Coding Contest) - Python, Windows

Ein Ordner pro Spiel (`Rock-Paper-Scissors/`, `Asteroid-Mining/`, `School-Magic-Money/`), Werkzeuge in `_template/`.
Jedes Spiel hat eine eigene `CLAUDE.md` (Regeln, Input-Struktur, Log, Fehler). Bei Problemen dort nach ähnlichen Fehlern suchen.
Ziel: jedes Level schnell und korrekt. Kurz antworten, nur bei echter Blockade nachfragen.

## Neues Spiel starten
1. `powershell -File _template\new_game.ps1 <Name>` (Name aus der Aufgabe), dann `cd <Name>`.
2. Wächter durchgehend von Start bis Ende: Monitor-Tool mit `powershell -NoProfile -File <Name>/watch_zips.ps1`
   (timeout 30 min, bei Ablauf SOFORT neu starten). Er meldet jede neue .zip (Prüfung alle 0,1 s).
3. Level 1: Ablauf unten. Die Spiel-`CLAUDE.md` laufend mit Regeln/Input-Struktur/Log füllen.

## Ablauf pro Level
1. Neues Zip gemeldet -> `close_output.ps1` -> `python run.py setup N "<zip>"` (entpackt flach, rendert PDF-Seiten
   nach `levelN/pages/*.png`, zeigt Input-Größen, legt `levelN.py` an: Kopie des vorigen Levels, bei Level 1 das Template).
2. ALLE PDF-Seiten als Bild ansehen (Regeln/Diagramme stehen oft nur als Bild, `pdftotext` ist unvollständig).
   2-3 Sätze Zusammenfassung mit Format und Randfällen, nicht auf Antwort warten.
3. Input-Größen ansehen (`python run.py info N`), Algorithmus danach wählen (Regel 2).
4. `levelN.py` erweitern. Mehrere gültige Lösungen? ZUERST `validate(inp, out)` schreiben (Regel 3).
5. `python run.py N` nach jeder Änderung: Beispiel, dann alle Inputs mit Laufzeit; Warnung ab 10 s.
6. Fertig = Beispiel OK + alle Outputs + keine Langsam-Warnung. Dann `git add -A` und commit "<Spiel> Level N".
7. `powershell -File open_output.ps1 N` (Explorer links, schließt alte Fenster), nur den Pfad melden.
   Der Nutzer zieht alle `out_*.txt` auf die Seite. Danach auf das nächste Zip warten.

## Plattform-Fakten
- Dateien `in_level-N_X-name.txt` / `out_level-N_X-name.txt`, je Level Beispiel (`_0-example`) + small + large.
  Beschreibung `level-N.pdf` (Folien), manchmal `sandbox-level-N.html` (Visualizer).
- Output exakt wie im Beispiel-Output (Leerzeilen am Ende mit `od -c` prüfen). Keine Output-Zips (nur `--zip`).
- Das Spiel steckt in einem Cross-Origin-iFrame: Upload per Browser-Tool unmöglich, der Nutzer lädt selbst hoch.
  Browser des Nutzers: Brave. Nie selbst einloggen, nur nach ausdrücklichem Ja herunterladen/abgeben.
- Browser-Start: Cookie-Dialog ablehnen, "How to Play" nach unten scrollen -> Close, oben "Download Level N".
- Zips heißen oft `level-N (1).zip`. Gleiche Dateien wie ein früheres Level = Kopie, kein neues Level.

## Allgemeine Learnings
1. Erst alle PDF-Seiten als Bild lesen, dann coden. Beispiel-Output nie hardcoden.
2. Vor dem Coden small/large-Größen ansehen: large ist 10-1000x größer. Algorithmus danach wählen
   (O(n^2) bei n=1e5 oder Beträge bis 1e9 brauchen Formel/DP/Tabelle), lieber iterativ als tief rekursiv.
3. Mehrere gültige Lösungen ("Generate", "any", Limit): zuerst Validator (Simulation, Limit, Format), nicht exakt vergleichen.
4. Steht im Input ein Limit/"Optimum": Limits der small-Datei verraten die Optimalität und den Zielwert.
5. Zustandsraumsuche, die in Python zu langsam ist (Millionen Zustände): in Java auslagern (JDK 21 ist installiert, `javac`/`java` im PATH), Python ruft per subprocess auf. Gewichtetes A* + zulässige BFS-Heuristik. Bei Rechenlimit größere Gewichte probieren.
5b. Konstruktion/Optimierung mit exakten Anzahlen: nicht Greedy/Zufall raten. Kleine Fälle per Brute-Force oder ILP
   (`scipy.optimize.milp`, installiert) lösen, Struktur ablesen, dann Formel oder DP.
6. Laufzeit: Kandidaten nach unterer Schranke sortieren, früh abbrechen, teure Checks nicht je Kandidat
   über das ganze Raster. Jede Datei > 10 s ist ein Warnsignal.
7. Nach jeder Änderung `python run.py N`. Level ist erst fertig mit allen Outputs. Danach committen.
8. Folge-Level erweitern statt neu schreiben; `solve(data)` rein, Regeln in kleinen Funktionen.
9. Gleicher Fehler 3-mal: Beschreibung neu lesen und Unklarheit benennen, nicht weiter raten.
10. Python-Dateien nur mit Write/Edit schreiben, nie per Bash-Heredoc (`\n` wird zerstört -> SyntaxError).
11. Windows: Explorer nur per PowerShell (`open_output.ps1`), Temp-Skripte in den Scratchpad (bash-`/tmp` ≠ Python-`/tmp`),
    `PYTHONUTF8=1` und `\r\n` normalisieren (macht `run.py`).
12. Der Wächter muss durchgehend laufen; Monitor läuft nach 30 min ab und wird sofort neu gestartet.
13. Seite meldet falsch, Fehler "got 'import sys'" = Lösungsdatei statt Output hochgeladen. Sonst Fehlfall-Screenshot des Nutzers nutzen.
14. Spielspezifisches nur in `<Spiel>/CLAUDE.md`. Am Spielende Log und Fehler dort ergänzen, allgemeine Regeln hier.

## Tools (`_template/`, spielunabhängig)
`run.py` (setup/info/run, exakt oder `validate`, Laufzeit, Timeout, `--zip`), `level_template.py`, `open_output.ps1`,
`close_output.ps1`, `watch_zips.ps1`, `new_game.ps1`. Verbesserungen in `_template` UND im aktiven Spiel pflegen.
