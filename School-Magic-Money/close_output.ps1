# Schliesst alle Explorer-Fenster, die einen levelN\output-Ordner dieses Projekts zeigen.
$root = $PSScriptRoot.TrimEnd('\')
$sh = New-Object -ComObject Shell.Application
foreach ($w in @($sh.Windows())) {
  try {
    $p = $w.Document.Folder.Self.Path
    if ($p -and $p.StartsWith($root, [StringComparison]::OrdinalIgnoreCase) -and $p -match '\\level\d+\\output$') { $w.Quit() }
  } catch {}
}
