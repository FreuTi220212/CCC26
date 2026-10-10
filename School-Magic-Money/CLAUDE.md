# School-Magic-Money (CCC 2024.04 School, Level 1-5, abgeschlossen)

Allgemeine Regeln stehen in `../CLAUDE.md`. Hier nur Spielspezifisches. Es gibt kein large-Laufzeitproblem (alle Inputs < 3 s).

## Regeln und Input-Struktur
- Währungen = Münzwerte. Level 1: `N`, `C`, N Zeilen mit C sortierten Werten -> kleinster positiver Betrag, der nicht als einzelne Münze existiert.
- Level 2: `N C A`, je Währung Münzzeile + Betragszeile -> je Betrag zwei Münzen (auch gleiche) mit Summe = Betrag, Ausgabe `x y` (kleinere zuerst). Mehrere Lösungen.
- Level 3: Input wie Level 1; je Währung alle Beträge 1..100 mit minimaler Münzzahl (unbegrenzt, DP). Ausgabe 100 Zeilen je Währung, `kxv` je Münzwert, absteigend.
- Level 4: Format wie Level 2, Beträge bis ~1e9. Größte Münze M: mindestens (A-LIM)//M+1 Kopien nehmen, Rest (LIM=2*M^2) per DP-Tabelle. Gegenprobe mit anderer Tabellengröße.
- Level 5: begrenzter Vorrat, Inventarzeile `nxv`-Tokens. Größter Wert M: entweder x_M in [n-M+2, n] (rekursiv, Memo über (Ebene, Rest)) oder höchstens M-1 kleinere Münzen (DP-Tabelle). Gegen Brute-Force an 3000 Zufallsfällen geprüft.

## Log
- Alle 5 Level je 1 Versuch bis `validate` OK. Beispiel-Output weicht bei mehreren Lösungen ab (gleiche Münzzahl) -> ok.
- Fehler: `\n` per Bash-Heredoc zerstörte Quelltext (wieder in L3). Auto-Upload unmöglich (Spiel im Cross-Origin-iFrame), Nutzer zieht Dateien selbst aus dem Explorer.
- Download-Zips hießen `level-N (1).zip`; Browser-Start: Cookie-Dialog ablehnen, "How to Play" nach unten scrollen und "Close".
- Level 5 brauchte die meiste Denkzeit (Tausch-Argument für begrenzten Vorrat).
