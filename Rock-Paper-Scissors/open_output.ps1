# Oeffnet levelN\output im Explorer auf der linken Bildschirmhaelfte. Aufruf: powershell -File open_output.ps1 N
param([int]$N)
$path = (Resolve-Path "$PSScriptRoot\level$N\output").Path
if (Test-Path "$PSScriptRoot\close_output.ps1") { & "$PSScriptRoot\close_output.ps1" }  # alte Output-Fenster zu
Start-Process explorer.exe -ArgumentList $path
Add-Type -AssemblyName System.Windows.Forms
$wa = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$sh = New-Object -ComObject Shell.Application
for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Milliseconds 300
  $w = $sh.Windows() | Where-Object { try { $_.Document.Folder.Self.Path -eq $path } catch { $false } } | Select-Object -First 1
  if ($w) { $w.Left = $wa.Left; $w.Top = $wa.Top; $w.Width = [int]($wa.Width / 2); $w.Height = $wa.Height; break }
}
