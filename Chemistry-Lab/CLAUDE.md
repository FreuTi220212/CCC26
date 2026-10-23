# Chemistry-Lab (CCC Live-Contest, Level 1-3, Platz 18)

Allgemeine Regeln: ../CLAUDE.md. Hier nur Spielregeln, Input je Level, Fehler/Zeitfresser.

## Regeln und Input-Struktur
- Molekuel-Listen `3 H2, 4 O2`, Reaktionen `A -> B`. Inventar-Reihenfolge = Einfuege-Reihenfolge; Menge 0 bleibt an ihrem Platz, wird nur nicht ausgegeben.
- L1: Reaktion einmal ausfuehren, Inventar ausgeben.
- L2: Preise `cost -> molecule`; Inventar startet leer, fehlende Edukte werden beim Ausfuehren zum Preis gekauft. Ausgabe `Kosten -> Inventar`.
- L3: Ziel `count name` (nie kaufbar), Ausgabe = Reaktionsfolge je Ziel (Absatz, Leerzeile, Datei endet mit Leerzeile). **Score = Summe der Kaufkosten (weniger ist besser, Bestenliste)**, Kosten exakt wie L2 simuliert.

## Was in L3 den Score gebracht hat (185896 -> 107912)
1. Greedy (je Molekuel billigste Reaktion nach Einheitskosten): 185896 = Platz der Durchschnittsteams.
2. Lokale Suche ueber "welche Reaktion erzeugt Molekuel m": ~142k.
3. ILP ueber Reaktionsanzahlen + Startbestand (`opt.py`-Ansatz): Bilanz allein ist NICHT ausfuehrbar (Katalysatoren/Kreislaeufe wie Ti/TiO2, CaO-Schleife, FeCl2/FeCl3, MnO/MnO2, Pt brauchen Startbestand). Loesung: Startbestand fuer JEDES Molekuel erlauben (nicht kaufbare zu Herstellkosten), **Atom-Bedingung** (braucht eine Reaktion k Atome eines Elements, muessen vorher k Atome gekauft sein), danach Reaktionen feuern lassen, beim Haengen billigste Fehlmenge zukaufen, Plan per Simulation pruefen. small 32716 -> 27064.
4. Je Ziel das Minimum aus allen Kandidaten (eigene + Teammate-Outputs) nehmen, jeden Absatz einzeln simulieren und validieren.
- Untere Schranke (Bilanz-ILP ohne Reihenfolge) war 73777; Spitze der Bestenliste ~99.7k.

## Fehler und Zeitfresser
1. Zu lange Greedy/lokale Suche, bevor die Ausfuehrbarkeit (Startbestand) richtig modelliert war. Zeitlich geschichtetes ILP und Siphon-Schnitte waren zu langsam bzw. zu schwach.
2. Mehrfach `\n` per Bash-Heredoc/Python-Ersetzung zerstoert (SyntaxError). Auch in Hilfsskripten nur Write/Edit.
3. Abgebrochene Hintergrundlaeufe haben `run.py`-Outputs geloescht (run.py leert den Output-Ordner beim Start): beste Outputs vorher sichern.
4. Bei Optimierungs-Leveln laufender Merge "je Ziel das Minimum" + Validator = immer hochladbare Datei.
