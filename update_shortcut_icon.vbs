Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")

' Create new PokerLab RNG shortcut
Set oLink = WshShell.CreateShortcut(strDesktop & "\PokerLab RNG.lnk")
oLink.TargetPath = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng\PokerLabRNG.exe"
oLink.WorkingDirectory = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng"
oLink.IconLocation = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng\icon.ico, 0"
oLink.Description = "PokerLab RNG — GTO Decision Engine"
oLink.Save

' Also update Poker RNG.lnk just in case the user clicks the old one
Set oLinkOld = WshShell.CreateShortcut(strDesktop & "\Poker RNG.lnk")
oLinkOld.TargetPath = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng\PokerLabRNG.exe"
oLinkOld.WorkingDirectory = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng"
oLinkOld.IconLocation = "C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng\icon.ico, 0"
oLinkOld.Description = "PokerLab RNG — GTO Decision Engine"
oLinkOld.Save

WScript.Echo "Genvej opdateret: " & strDesktop & "\PokerLab RNG.lnk"
