# Neues Spiel anlegen: powershell -File _template\new_game.ps1 <Ordnername>
# Kopiert alle Werkzeuge aus _template in C:\_repos\CCC26\<Ordnername>\ und legt eine leere CLAUDE.md fuer das Spiel an.
param([Parameter(Mandatory = $true)][string]$Name)
$root = Split-Path $PSScriptRoot -Parent
$dest = Join-Path $root $Name
if (Test-Path $dest) { Write-Error "$dest existiert schon"; exit 1 }
New-Item -ItemType Directory $dest | Out-Null
Get-ChildItem $PSScriptRoot -File | Where-Object { $_.Name -notin @('new_game.ps1', 'README.md') } | Copy-Item -Destination $dest
$md = "# $Name`n`nAllgemeine Regeln: ../CLAUDE.md. Hier nur Spielregeln, Input-Struktur je Level und Log.`n`n## Regeln und Input-Struktur`n`n## Log`n"
Set-Content -Path (Join-Path $dest 'CLAUDE.md') -Value $md -Encoding UTF8
Write-Output $dest
