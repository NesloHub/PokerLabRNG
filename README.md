# PokerLab RNG — High-Performance GTO Desktop HUD

An ultra-compact, high-performance desktop HUD engineered for poker players using mixed frequencies (GTO strategies), multi-tabling, and live games.

Built with **PyQt6** for 144Hz/240Hz silky smooth window movement, fixed HUD dimensions, single-trigger **Hover Mode**, and cryptographically secure random number generation (CSPRNG).

---

## ⚡ Quick Start

1. **Directly from your Desktop**:
   - Double-click the **`PokerLab RNG.lnk`** shortcut on your Desktop!
2. **Or from the directory**:
   - Double-click [`PokerLabRNG.exe`](file:///C:/Users/Neslo/.gemini/antigravity-ide/scratch/poker-rng/PokerLabRNG.exe)
   - Or run [`Start-PokerRNG.bat`](file:///C:/Users/Neslo/.gemini/antigravity-ide/scratch/poker-rng/Start-PokerRNG.bat)

---

## 🎯 Key Features & Details

- **Integrated Brand & Icon Inside the Program**:
  - The header displays the custom glowing neon spade chip icon alongside the title **`POKERLAB RNG`**.
- **Fixed HUD Footprint (240 × 420 px)**:
  - Non-resizable, compact layout designed to sit cleanly beside or between your poker tables (PokerStars, GGPoker, PartyPoker, Unibet, WPT, etc.).
- **144Hz / 240Hz Silky Smooth Performance**:
  - Zero lag or stutter when moving the window across monitors or between active tables.
  - Asynchronous audio playback prevents any GUI thread blocking.
- **🔥 Single-Sweep Hover Mode**:
  - Turn on **Hover**, and the RNG will roll automatically exactly ONCE each time the mouse cursor sweeps across the card. Zero clicks and zero keystrokes required!
- **📌 Always on Top (Pin)**:
  - Enabled by default, ensuring PokerLab RNG never hides behind active poker tables.
- **Cryptographically Secure (CSPRNG)**:
  - Mathematically unbiased, uniform random generation (1–100) powered by Python `secrets`.
- **GTO Frequency Decision Evaluator**:
  - Preset buttons for standard GTO frequencies (**25%**, **33%**, **50%**, **75%**) plus a precision slider.
  - Automatically highlights **`BET / RAISE (≤ X%)`** in glowing green if roll is within threshold, or **`CHECK / FOLD (> X%)`** in muted slate if above.
- **Auto-Roll or Manual**:
  - Choose between *Manual*, *Hover*, *Auto 2s*, or *Auto 1s*.
- **Roll History & Stats**:
  - Displays the last 6 rolls with action color coding and running average.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| **Spacebar** | Roll new number manually |
| **H** | Toggle **Hover Mode** on/off |
| **A** | Toggle Auto-Roll on/off |
| **T** | Toggle "Always on Top" (Pin 📌) |
| **M** | Toggle sound (Mute/Unmute) |
| **Up / Down** | Adjust threshold (+/- 5%) |

---

## 📁 Project Files

- Executable: [`PokerLabRNG.exe`](file:///C:/Users/Neslo/.gemini/antigravity-ide/scratch/poker-rng/PokerLabRNG.exe)
- Source code: [`poker_rng_qt.pyw`](file:///C:/Users/Neslo/.gemini/antigravity-ide/scratch/poker-rng/poker_rng_qt.pyw)
- Release Zip: [`PokerLab_RNG_v1.0.zip`](file:///C:/Users/Neslo/.gemini/antigravity-ide/scratch/poker-rng/PokerLab_RNG_v1.0.zip)
- Desktop Shortcut: `C:\Users\Neslo\Desktop\PokerLab RNG.lnk`
