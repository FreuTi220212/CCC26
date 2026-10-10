# Migratory-Birds (CCC Data & AI, Level 1-6, abgeschlossen)

Allgemeine Regeln: ../CLAUDE.md. Hier nur Spielregeln, Input je Level, Fehler/Zeitfresser. Daten-/ML-Spiel: numpy, kein Algorithmus-Wettbewerb.
Orte = BOPs (Nr. 1..2500, 50x50, aber ohne räumliche Struktur nutzbar). Pro Level: Beispiel + 1 Hauptdatei (Bewertung nur per Plattform-Upload).

## Regeln und Input-Struktur
- Zahlen in CSVs teils als Wörter ("seventeen") -> `to_int`. Temperatur > 55 ist °F (Fehler im Datensatz) -> (t-32)*5/9. Beispiel-Outputs oft OHNE Schluss-Newline.
- L1: BOPs nach Beliebtheit sortieren: Schlüssel `(-Temp, Luftfeuchte, BOP)`.
- L2: "Bird Love Score" je BOP: lineare Regression (lstsq) auf [1, Temp, Feuchte, Insekten, Urban, Vegetation] mit den bekannten Zeilen aller Level-2-Dateien.
- L3: Schwarm -> Art (je Datei genau ein Schwarm pro Art): Bluetit = identische, palindromische Pfade, LÄNGERE Route; Wolfthroat = Anteil eigener Knoten auf der Bluetit-Route; Blackfinch = identisch, geschlossen, nicht palindromisch; Hurracurra = höchste Temperatur; Goldhammer = längstes gemeinsames Präfix; Firefinch = Rest.
- L4: Arten für ungelabelte Schwärme aus Merkmalen (Entscheidungsliste, an 288 Labels abgestimmt, 284 richtig); Ausgabe nur die fehlenden Schwärme.
- L5: Top-50 Arrivals je Tag 731..760 (Schwelle 0.5): NUR Occupancy des Prognosetages als Ranking besteht (Plattform-Test). Verhältnis-Modelle (0.496, 0.4287) und alle Backtests täuschten.
- L6: Top-50 für Tag 791, Schwelle 100 %. **Tage 761..790 sind die exakte Spiegelung der Tage 760..731 (Zeit rückwärts, Wind negiert). Tag 791 = Tag 730 aus `all_data_from_level_5.in`.** Output = Top-50 Arrivals von Tag 730.

## Fehler und Zeitfresser (Reihenfolge nach verlorener Zeit)
1. L6: Stunden mit statistischen Prognosen (Persistenz 0.90-0.92, Regression, Graph-Transport), obwohl 100 % verlangt war. 100 % = deterministisch -> Spiegelung. Gefunden erst durch die Tag-für-Tag-Tabelle "ähnlichster früherer Tag" (L1-Abstand 0) und identische Tagessummen.
2. L5: drei Plattform-Versuche, weil Backtests auf Trainingstagen das Ergebnis falsch einschätzten. Einfachste Variante zuerst hochladen.
3. L3: Bluetit/Wolfthroat vertauscht (macro-F1 0.6667) -> längere Route = Bluetit.
4. L5: `np.fromstring` 68 s für 58 MB; `np.loadtxt(StringIO)` 1.6 s.
5. Explorer-Skript schloss/übersprang Fenster -> jetzt immer neues Fenster links, nie schließen.
6. Wiederholt: `\n` per Bash-Heredoc, `cat > file` ohne stdin hängt 120 s (Write-Tool benutzen).
