# Oeffnet levelN\output im Explorer auf der linken Bildschirmhaelfte, falls dort nicht schon ein Fenster offen ist.
# Schliesst nie etwas (der Nutzer schliesst Fenster selbst). Aufruf: powershell -File open_output.ps1 N
param([int]$N)
$path = (Resolve-Path "$PSScriptRoot\level$N\output").Path
$sh = New-Object -ComObject Shell.Application
function Find-Win { $sh.Windows() | Where-Object { try { $_.Document.Folder.Self.Path -eq $path } catch { $false } } | Select-Object -First 1 }
if (Find-Win) { return }  # schon offen: nicht doppelt oeffnen
Start-Process explorer.exe -ArgumentList $path
Add-Type -AssemblyName System.Windows.Forms
$wa = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Milliseconds 100
  $w = Find-Win
  if ($w) { $w.Left = $wa.Left; $w.Top = $wa.Top; $w.Width = [int]($wa.Width / 2); $w.Height = $wa.Height; break }
}
