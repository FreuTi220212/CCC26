# Oeffnet levelN\output IMMER in einem NEUEN Explorer-Fenster auf der linken Bildschirmhaelfte (Aufruf: einmal je Output-Satz).
# Schliesst nie etwas (der Nutzer schliesst Fenster selbst). Aufruf: powershell -File open_output.ps1 N
param([int]$N)
$path = (Resolve-Path "$PSScriptRoot\level$N\output").Path
$sh = New-Object -ComObject Shell.Application
function Wins { @($sh.Windows() | Where-Object { try { $_.Document.Folder.Self.Path -eq $path } catch { $false } }) }
$before = @(Wins | ForEach-Object { $_.HWND })
Start-Process explorer.exe -ArgumentList $path
Add-Type -AssemblyName System.Windows.Forms
$wa = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Milliseconds 100
  $w = Wins | Where-Object { $before -notcontains $_.HWND } | Select-Object -First 1
  if ($w) { $w.Left = $wa.Left; $w.Top = $wa.Top; $w.Width = [int]($wa.Width / 2); $w.Height = $wa.Height; break }
}
