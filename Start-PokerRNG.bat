@echo off
if exist "%~dp0PokerLabRNG.exe" (
    start "" "%~dp0PokerLabRNG.exe"
    exit
)
if exist "%~dp0PokerRNG.exe" (
    start "" "%~dp0PokerRNG.exe"
    exit
)
start "" pythonw "%~dp0poker_rng_qt.pyw"
exit
