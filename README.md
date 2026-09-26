# PokerLab RNG

A small Windows program that rolls a random number from **1 to 100**.

It is built for players who mix their frequencies (the GTO way of playing): you decide how often you
want to bet or raise — say 50 % — and the program rolls the number for you. That way the decision is
random and honest instead of "I think I feel like raising this time".

It is **not** a tracker, not a HUD and not a solver. It does not read your tables, does not count
hands, stores no statistics and never goes online. It only rolls a number.

---

## Download and run

1. Open the [latest release](https://github.com/NesloHub/PokerLabRNG/releases/latest) and download
   `PokerLab_RNG_v1.0.zip`.
2. Unzip it anywhere (Desktop is fine).
3. Double-click **`PokerLabRNG.exe`**.

Nothing to install: no admin rights, no account, no internet connection. Windows 10 or 11, 64-bit.
The window is a fixed 240 x 420 px and stays on top of your tables — drag it wherever it suits you.

---

## Using it — three steps

1. **Set your frequency.** Click **25 %**, **33 %**, **50 %** or **75 %**, or drag the slider to any
   value between 1 and 100.
2. **Roll.** Press the big **ROLL RNG** button, the **space bar**, or click the number card itself.
3. **Read the answer.** The program compares the roll with your frequency:
   - roll **inside** your frequency → **BET / RAISE (≤ 50 %)** shown in green
   - roll **above** your frequency → **CHECK / FOLD (> 50 %)** shown in grey

With a frequency of 50 %, a roll of **12** means BET / RAISE and a roll of **58** means CHECK / FOLD.

---

## What you see on screen

| Part of the window | What it does |
| :--- | :--- |
| The big number | The latest roll, from 1 to 100. Click the card to roll again. |
| Green or grey line under the number | The action that follows from the roll and your frequency. |
| **ROLL RNG (Space)** | Rolls a new number. |
| **Manual / Hover / Auto 2s / Auto 1s** | How rolls happen: only when you ask (Manual), once every time the mouse sweeps over the card (Hover), or on a timer. |
| **Threshold** + slider | Your frequency in percent. |
| **25 % / 33 % / 50 % / 75 %** | Quick buttons for the most common frequencies. |
| The row of small boxes | Your last six rolls. |
| **Rolls: n | Avg: x.x** | How many rolls this session and their average. |
| Speaker button | Sound on or off. |
| Pin button | Keep the window on top — on by default. |

---

## Keyboard shortcuts

| Key | Action |
| :--- | :--- |
| **Space** | Roll a new number |
| **H** | Turn Hover mode on or off |
| **A** | Turn Auto-roll (2 s) on or off |
| **T** | Turn "always on top" on or off |
| **M** | Mute or unmute the sound |
| **Up / Down** | Frequency +/- 5 % |

---

## Good to know

- The rolls are cryptographically random (Python `secrets`), so every number from 1 to 100 is equally
  likely. There is no pattern to exploit — a low roll does not make a high roll more likely.
- Nothing is saved to disk. Close the program and the history is gone; the next start begins fresh.
- The sound is a short beep. It plays on a background thread, so it never makes the window stutter.
- The download is about 38 MB because the program ships with everything it needs (PyQt6) inside one
  EXE — there is nothing else to install.

---

## Run or build it yourself

Run from the source:

```bat
python -m pip install PyQt6
python poker_rng_qt.pyw
```

Build the single-file EXE again:

```bat
python -m pip install pyinstaller
pyinstaller PokerLabRNG.spec
```

The finished program is written to `dist\PokerLabRNG.exe`.

---

## Files in this repository

| File | What it is |
| :--- | :--- |
| `poker_rng_qt.pyw` | The program — the PyQt6 version that is released. |
| `PokerLabRNG.spec` | PyInstaller recipe used to build `PokerLabRNG.exe`. |
| `icon.ico`, `icon.png` | The program icon. |
| `release_files/` | `README.txt` and `Start.bat`, the two extra files that go into the release zip. |
| `build_zip.py` | Builds the release zip from the EXE and `release_files/`. |
| `poker_rng.pyw`, `PokerRNG.spec` | Earlier Tkinter prototype, kept for reference. |
| `index.html`, `style.css`, `app.js` | A browser mock-up of the same tool — not part of the EXE. |
| `create_shortcut.ps1`, `create_shortcut.vbs`, `update_shortcut_icon.vbs` | Helpers that put a shortcut with the right icon on the Desktop. |

