======================================================================
 POKERLAB RNG  (v1.0)
 A small random number generator for GTO mixed frequencies
======================================================================

WHAT IT DOES
------------
PokerLab RNG rolls a random number from 1 to 100. You set how often you
want to bet or raise (your frequency), and the program rolls the number
so the decision is random and honest instead of a feeling.

It is NOT a tracker, NOT a HUD and NOT a solver. It does not read your
tables, does not count hands, stores no statistics and never goes online.
It only rolls a number.


START IT
--------
1. Unzip this package anywhere you like (the Desktop is fine).
2. Double-click  PokerLabRNG.exe

Nothing to install: no admin rights, no account, no internet connection.
Windows 10 or 11, 64-bit.
The window is a fixed 240 x 420 px and stays on top of your tables.
Drag it wherever it suits you.


USE IT - THREE STEPS
--------------------
1. SET YOUR FREQUENCY
   Click 25 %, 33 %, 50 % or 75 %, or drag the slider to any value
   between 1 and 100.

2. ROLL
   Press the big ROLL RNG button, the space bar, or click the number
   card itself.

3. READ THE ANSWER
   The program compares the roll with your frequency:
     - roll inside your frequency  ->  BET / RAISE (<= 50 %)  in green
     - roll above your frequency   ->  CHECK / FOLD (> 50 %)  in grey

   With a frequency of 50 %, a roll of 12 means BET / RAISE and a roll
   of 58 means CHECK / FOLD.


WHAT YOU SEE ON SCREEN
----------------------
  The big number ......... the latest roll (1-100). Click the card to
                           roll again.
  Green or grey line ..... the action that follows from the roll and
                           your frequency.
  ROLL RNG (Space) ....... rolls a new number.
  Manual / Hover /
  Auto 2s / Auto 1s ...... how rolls happen: only when you ask
                           (Manual), once every time the mouse sweeps
                           over the card (Hover), or on a timer.
  Threshold + slider ..... your frequency in percent.
  25 / 33 / 50 / 75 % .... quick buttons for common frequencies.
  Row of small boxes ..... your last six rolls.
  Rolls / Avg ............ how many rolls this session and their
                           average.
  Speaker button ......... sound on or off.
  Pin button ............. keep the window on top (on by default).


KEYBOARD SHORTCUTS
------------------
  Space ................ roll a new number
  H .................... turn Hover mode on or off
  A .................... turn Auto-roll (2 s) on or off
  T .................... turn "always on top" on or off
  M .................... mute or unmute the sound
  Up / Down ............ frequency +/- 5 %


GOOD TO KNOW
------------
- The rolls are cryptographically random, so every number from 1 to 100
  is equally likely. A low roll does not make a high roll more likely.
- Nothing is saved to disk. Close the program and the history is gone.
- The sound is a short beep, played on a background thread so it never
  makes the window stutter.

======================================================================
 Made with PokerLab Engine. Good luck at the tables!
======================================================================
