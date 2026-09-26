Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oLink = WshShell.CreateShortcut(strDesktop & "\Poker RNG.lnk")
oLink.TargetPath = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng\PokerRNG.exe"
oLink.WorkingDirectory = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng"
oLink.Description = "Poker RNG Decision Engine"
oLink.Save
WScript.Echo "Genvej oprettet: " & strDesktop & "\Poker RNG.lnk"
