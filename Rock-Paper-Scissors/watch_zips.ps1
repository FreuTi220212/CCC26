# Durchgehender Wächter: prüft alle 0,1 s den Downloads-Ordner und gibt für JEDE neue .zip genau eine Zeile (den Pfad) aus.
# Läuft endlos (für das Monitor-Tool); beendet sich nie von selbst.
$dl = Join-Path $env:USERPROFILE "Downloads"
$seen = @{}
Get-ChildItem "$dl\*.zip" -ErrorAction SilentlyContinue | ForEach-Object { $seen[$_.FullName] = $true }
while ($true) {
  foreach ($z in @(Get-ChildItem "$dl\*.zip" -ErrorAction SilentlyContinue)) {
    if (-not $seen.ContainsKey($z.FullName)) {
      $seen[$z.FullName] = $true
      Start-Sleep -Seconds 2   # Download fertig schreiben lassen
      [Console]::Out.WriteLine($z.FullName)
      [Console]::Out.Flush()
    }
  }
  Start-Sleep -Milliseconds 100
}
