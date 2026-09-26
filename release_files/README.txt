========================================================================
POKERLAB RNG — GTO DECISION HUD (v1.0)
========================================================================

Welcome to PokerLab RNG!
An ultra-compact, high-performance desktop HUD designed for poker players
using mixed-frequency strategies (GTO), multi-tabling, and live games.

100% Standalone — No installation required! Just extract and play.

------------------------------------------------------------------------
QUICK START
------------------------------------------------------------------------
Double-click:
  PokerLabRNG.exe

(Optional: Right-click PokerLabRNG.exe -> "Create shortcut" and drag it 
to your Desktop).


------------------------------------------------------------------------
KEY FEATURES
------------------------------------------------------------------------
1. Fixed HUD Footprint (240 x 420 px):
   Compact size designed to sit cleanly beside or between your poker 
   tables (PokerStars, GGPoker, PartyPoker, WPT, etc.) without obstructing
   cards, chips, or action buttons.

2. 144Hz / 240Hz Silky Smooth Movement:
   Engineered with PyQt6 for perfectly fluid window dragging across 
   monitors and tables with zero stutter.

3. Single-Sweep Hover Mode:
   Enable "Hover", and the RNG will roll automatically exactly ONCE 
   each time your mouse cursor sweeps across the card. Zero clicks and
   zero keystrokes required during high-speed multi-tabling!

4. Always on Top (Pin 📌):
   Enabled by default so PokerLab RNG never hides behind active poker 
   clients when you click and bet.

5. Cryptographically Secure (CSPRNG):
   Uses Python `secrets` for unbiased, perfectly uniform random number
   generation (1–100).

6. GTO Frequency Decision Evaluator:
   Quick preset chips for standard GTO frequencies (25%, 33%, 50%, 75%)
   plus a precision slider.
   Instantly displays:
     - Glowing Green "BET / RAISE (<= X%)" if roll <= your threshold.
     - Muted Slate "CHECK / FOLD (> X%)" if roll > your threshold.

7. Auto-Roll Timer:
   Continuous rolling every 1s or 2s for glance-and-go decision making.

8. Roll History & Running Average:
   Shows the last 6 rolls with action color coding and running average.


------------------------------------------------------------------------
KEYBOARD SHORTCUTS
------------------------------------------------------------------------
  Spacebar           : Roll new number manually
  H                  : Toggle Hover Mode on/off
  A                  : Toggle Auto-Roll (2s) on/off
  T                  : Toggle Always On Top (Pin 📌)
  M                  : Toggle Sound (Mute/Unmute)
  Up Arrow / Down    : Adjust threshold (+/- 5%)

========================================================================
Built with PokerLab Engine
Good luck at the tables!
========================================================================
