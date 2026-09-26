$desktop = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut((Join-Path $desktop "Poker RNG.lnk"))
$shortcut.TargetPath = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng\PokerRNG.exe"
$shortcut.WorkingDirectory = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng"
$shortcut.Description = "Poker RNG — GTO Decision Engine"
$shortcut.Save()
Write-Output "Genvej oprettet på Skrivebordet: $desktop\Poker RNG.lnk"
