# Wartet (Pruefung alle 0,1 s), bis im Downloads-Ordner eine neue .zip erscheint, die neuer ist als der Start. Gibt den Pfad aus.
$dl = Join-Path $env:USERPROFILE "Downloads"
$start = Get-Date
while ($true) {
  $z = Get-ChildItem "$dl\*.zip" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $start } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if ($z -and (Test-Path $z.FullName)) {
    Start-Sleep -Seconds 2   # Download fertig schreiben lassen
    $z = Get-Item $z.FullName
    Write-Output $z.FullName
    break
  }
  Start-Sleep -Milliseconds 100
}
