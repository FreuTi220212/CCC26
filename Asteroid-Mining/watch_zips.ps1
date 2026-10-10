# Durchgehender Waechter fuer das Monitor-Tool: gibt fuer JEDE neue .zip im Downloads-Ordner genau eine Zeile (den Pfad) aus.
# Prueft alle 20 ms; sobald die Datei vollstaendig lesbar ist (Browser benennt .crdownload erst am Ende um), wird gemeldet.
$dl = Join-Path $env:USERPROFILE "Downloads"
$seen = @{}
foreach ($f in [IO.Directory]::GetFiles($dl, "*.zip")) { $seen[$f] = 1 }
while ($true) {
  foreach ($f in [IO.Directory]::GetFiles($dl, "*.zip")) {
    if (-not $seen.ContainsKey($f)) {
      $seen[$f] = 1
      for ($i = 0; $i -lt 200; $i++) {  # max. 5 s warten, bis die Datei freigegeben ist
        try { $fs = [IO.File]::Open($f, 'Open', 'Read', 'None'); $fs.Close(); break } catch { Start-Sleep -Milliseconds 25 }
      }
      [Console]::Out.WriteLine($f)
      [Console]::Out.Flush()
    }
  }
  Start-Sleep -Milliseconds 20
}
