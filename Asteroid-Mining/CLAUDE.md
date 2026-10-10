# Asteroid-Mining (Level 1-5, abgeschlossen)

Allgemeine Regeln stehen in `../CLAUDE.md`. Hier nur Spielspezifisches. Pro Level nur 2 Inputs (small, large) + Beispiel; Ordner enthält `sandbox-level-N.html` (Visualizer).

## Regeln und Input-Struktur
- Raster: `#` Grundgestein, `:` minierbar, `S` Außenposten (Zeile 0), `X` Tunnel. Nach JEDEM Asteroiden eine Leerzeile (auch nach dem letzten, wie im Beispiel-Output).
- Level 1: `N`, `W H` -> Rechteck (W+2)x(H+2), außen `#`, innen `:`.
- Level 2: `N`, je Asteroid `W H` + (H+2) Rasterzeilen, W=3, `S` mittig -> Tunnel `X` senkrecht unter `S` bis vors Grundgestein.
- Level 3: je Asteroid `W H LIMIT` + Raster, W oder H = 3, `S` irgendwo in Zeile 0. Tunnel zusammenhängend (an `S`), jede minierbare Zelle Tunnel oder 4er-Nachbar eines Tunnels, höchstens LIMIT X-Zellen (S zählt nicht). Mittelspalte/-zeile + Anschlusszelle.
- Level 4: W oder H durch 3 teilbar, LIMIT = Optimum+1. Kamm: Rückgrat + Zinken in Dreiergruppen-Mitten, Anschluss als kürzester L-Weg von `(1,sc)` zur nächsten Kammzelle.
- Level 5: beliebig 3..199, LIMIT = exaktes Optimum. Rückgrat am Rand (Zeile/Spalte 1, 2, n-1, n), Zinken nur auf einer Seite mit Länge je Spalte in {0, H-1, H} (DP über die Spalten), Rückgrat an den Enden um 1 kürzbar (dort u=0), Anschluss `top`/`end`.
- Validator prüft Verbindung, Abdeckung und Limit (`check`). Solve prüft die Limits der Inputs selbst.

## Log
- L1: Leerzeile nach dem letzten Asteroiden fehlte -> Beispiel-Output mit `od -c` ansehen.
- L2: Regeln stehen nur als Bild auf PDF-Seite 2 (`pdftotext` unvollständig).
- L4: Anschluss entlang Zeile 1 war bis 51 Zellen zu teuer (Limits sind Opt+1) -> L-Weg zur nächsten Zinke. Alle Rückgrat-Positionen durchprobieren war 49 s -> Kandidaten einschränken (7 s).
- L5: Level-4-Kamm war 1 Zelle zu teuer (Beispiel 6x9: zwei Linien, Rückgrat nur ZWISCHEN den Zinken). Exaktes ILP (`exact_ilp.py`, scipy.milp + Fluss) für kleine Raster lieferte das Optimum, daraus Struktur abgelesen. Kandidaten nach unterer Schranke sortiert (sonst > 120 s), large ~6-8 s.
- Das Spiel wurde danach ein zweites Mal ab Level 2 durchgespielt (identische Zips), Outputs mit `run.py N` neu erzeugt.
