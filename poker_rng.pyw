#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poker RNG — Elegant Compact GTO Decision Engine
Native Windows Desktop Program for online poker multi-tabling.
"""

import sys
import os
import secrets
import threading
import time
import customtkinter as ctk

# Windows sound support
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# Setup Appearance & Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class PokerRNGApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup - Ultra compact for multi-tabling
        self.title("Poker RNG")
        self.geometry("250x420")
        self.minsize(230, 390)
        self.configure(fg_color="#090d16")

        # Core State
        self.min_val = 1
        self.max_val = 100
        self.threshold = 50
        self.current_roll = 50
        self.action_a_text = "BET / RAISE"
        self.action_b_text = "CHECK / FOLD"
        
        self.is_topmost = True
        self.is_muted = False
        self.is_auto = False
        self.auto_interval_sec = 2.0
        
        self.history = []  # List of (number, is_action_a)
        self.total_rolls = 0
        self.sum_rolls = 0

        # Auto-roll worker thread flag
        self._auto_thread_running = False

        # Set Always On Top by default (essential for poker tables)
        self.attributes("-topmost", self.is_topmost)

        # Build Interface
        self.build_ui()

        # Keyboard shortcuts
        self.bind("<space>", lambda event: self.execute_roll())
        self.bind("<a>", lambda event: self.toggle_auto_roll())
        self.bind("<m>", lambda event: self.toggle_mute())
        self.bind("<t>", lambda event: self.toggle_topmost())
        self.bind("<Up>", lambda event: self.adjust_threshold(5))
        self.bind("<Down>", lambda event: self.adjust_threshold(-5))

        # Initial Roll
        self.execute_roll(play_sound=False)

    def build_ui(self):
        # 1. Header Row (Title, Pin/Topmost, Sound)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=12, pady=(10, 4))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="POKER RNG",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#94a3b8"
        )
        self.title_label.pack(side="left")

        # Topmost Toggle (Pin)
        self.pin_btn = ctk.CTkButton(
            self.header_frame,
            text="📌",
            width=28,
            height=26,
            fg_color="#10b981" if self.is_topmost else "#1e293b",
            hover_color="#059669",
            text_color="#ffffff",
            font=ctk.CTkFont(size=12),
            command=self.toggle_topmost
        )
        self.pin_btn.pack(side="right", padx=(4, 0))

        # Sound Toggle
        self.sound_btn = ctk.CTkButton(
            self.header_frame,
            text="🔊",
            width=28,
            height=26,
            fg_color="#1e293b",
            hover_color="#334155",
            text_color="#94a3b8",
            font=ctk.CTkFont(size=12),
            command=self.toggle_mute
        )
        self.sound_btn.pack(side="right")

        # 2. Main Number Card
        self.card_frame = ctk.CTkFrame(
            self,
            fg_color="#0f172a",
            corner_radius=14,
            border_width=1,
            border_color="#1e293b"
        )
        self.card_frame.pack(fill="x", padx=12, pady=4)

        # Clickable dial area
        self.roll_label = ctk.CTkLabel(
            self.card_frame,
            text="50",
            font=ctk.CTkFont(family="Consolas", size=48, weight="bold"),
            text_color="#f8fafc"
        )
        self.roll_label.pack(pady=(8, 0))
        self.roll_label.bind("<Button-1>", lambda event: self.execute_roll())

        # Decision Badge (BET vs CHECK)
        self.badge_frame = ctk.CTkFrame(
            self.card_frame,
            fg_color="#064e3b",
            corner_radius=8,
            border_width=1,
            border_color="#10b981"
        )
        self.badge_frame.pack(pady=(2, 10), padx=16, fill="x")

        self.badge_text = ctk.CTkLabel(
            self.badge_frame,
            text="BET / RAISE  (≤ 50%)",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#10b981"
        )
        self.badge_text.pack(pady=3)

        # 3. Main Roll Button
        self.roll_btn = ctk.CTkButton(
            self,
            text="RUL RNG  (Space)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#022c22",
            height=34,
            corner_radius=10,
            command=self.execute_roll
        )
        self.roll_btn.pack(fill="x", padx=12, pady=4)

        # 4. Mode Selector (Manuelt vs Auto)
        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.pack(fill="x", padx=12, pady=(2, 4))

        self.mode_seg = ctk.CTkSegmentedButton(
            self.mode_frame,
            values=["Manuelt", "Auto 1s", "Auto 2s", "Auto 3s"],
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#0f172a",
            selected_color="#1e293b",
            selected_hover_color="#334155",
            unselected_color="#0f172a",
            unselected_hover_color="#1e293b",
            command=self.on_mode_change
        )
        self.mode_seg.set("Manuelt")
        self.mode_seg.pack(fill="x")

        # 5. GTO Frequency Threshold Slider & Presets
        self.freq_header = ctk.CTkFrame(self, fg_color="transparent")
        self.freq_header.pack(fill="x", padx=12, pady=(6, 2))

        self.freq_label = ctk.CTkLabel(
            self.freq_header,
            text="Tærskel:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#94a3b8"
        )
        self.freq_label.pack(side="left")

        self.freq_val_label = ctk.CTkLabel(
            self.freq_header,
            text="50%",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#10b981"
        )
        self.freq_val_label.pack(side="right")

        # Slider
        self.slider = ctk.CTkSlider(
            self,
            from_=0,
            to=100,
            number_of_steps=100,
            height=14,
            button_color="#10b981",
            button_hover_color="#059669",
            progress_color="#10b981",
            fg_color="#1e293b",
            command=self.on_slider_change
        )
        self.slider.set(self.threshold)
        self.slider.pack(fill="x", padx=12, pady=2)

        # Preset Chips (25%, 33%, 50%, 75%)
        self.presets_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.presets_frame.pack(fill="x", padx=12, pady=(2, 4))

        for p_val in [25, 33, 50, 75]:
            btn = ctk.CTkButton(
                self.presets_frame,
                text=f"{p_val}%",
                width=46,
                height=22,
                font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                fg_color="#0f172a",
                hover_color="#1e293b",
                border_width=1,
                border_color="#1e293b",
                text_color="#94a3b8",
                command=lambda v=p_val: self.set_threshold(v)
            )
            btn.pack(side="left", expand=True, padx=2)

        # 6. Mini History Row
        self.history_frame = ctk.CTkFrame(self, fg_color="#090d16")
        self.history_frame.pack(fill="x", padx=12, pady=(4, 6))

        self.history_labels_frame = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.history_labels_frame.pack(fill="x")

        # 7. Stats Footer
        self.stats_label = ctk.CTkLabel(
            self,
            text="Rul: 0  |  Snit: —",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color="#64748b"
        )
        self.stats_label.pack(side="bottom", pady=(0, 6))

    # -------------------------------------------------------------------------
    # Core Logic
    # -------------------------------------------------------------------------
    def execute_roll(self, play_sound=True):
        # Cryptographically secure random integer in [min_val, max_val]
        val = secrets.randbelow(self.max_val - self.min_val + 1) + self.min_val
        self.current_roll = val
        is_action_a = val <= self.threshold

        # Update Display
        self.roll_label.configure(text=str(val))

        # Update Badge
        if is_action_a:
            self.badge_frame.configure(fg_color="#064e3b", border_color="#10b981")
            self.badge_text.configure(
                text=f"{self.action_a_text} (≤ {self.threshold}%)",
                text_color="#10b981"
            )
            self.roll_label.configure(text_color="#10b981")
        else:
            self.badge_frame.configure(fg_color="#1e293b", border_color="#334155")
            self.badge_text.configure(
                text=f"{self.action_b_text} (> {self.threshold}%)",
                text_color="#94a3b8"
            )
            self.roll_label.configure(text_color="#f8fafc")

        # Sound
        if play_sound and not self.is_muted and HAS_WINSOUND:
            try:
                # Ascending frequency for action A, subtle click for action B
                freq = 880 if is_action_a else 440
                winsound.Beep(freq, 40)
            except Exception:
                pass

        # Update History & Stats
        self.total_rolls += 1
        self.sum_rolls += val
        self.history.insert(0, (val, is_action_a))
        if len(self.history) > 6:
            self.history.pop()

        self.update_history_ui()
        self.update_stats_ui()

    def update_history_ui(self):
        for widget in self.history_labels_frame.winfo_children():
            widget.destroy()

        for num, is_a in self.history:
            lbl = ctk.CTkLabel(
                self.history_labels_frame,
                text=f"{num:02d}",
                width=30,
                height=18,
                corner_radius=4,
                fg_color="#064e3b" if is_a else "#1e293b",
                text_color="#10b981" if is_a else "#94a3b8",
                font=ctk.CTkFont(family="Consolas", size=9, weight="bold")
            )
            lbl.pack(side="left", padx=2, expand=True)

    def update_stats_ui(self):
        if self.total_rolls > 0:
            avg = self.sum_rolls / self.total_rolls
            self.stats_label.configure(text=f"Rul: {self.total_rolls}  |  Snit: {avg:.1f}")

    # -------------------------------------------------------------------------
    # Threshold Controls
    # -------------------------------------------------------------------------
    def on_slider_change(self, val):
        self.set_threshold(int(val))

    def set_threshold(self, val):
        self.threshold = max(0, min(100, int(val)))
        self.slider.set(self.threshold)
        self.freq_val_label.configure(text=f"{self.threshold}%")

        # Re-evaluate current roll against new threshold
        is_action_a = self.current_roll <= self.threshold
        if is_action_a:
            self.badge_frame.configure(fg_color="#064e3b", border_color="#10b981")
            self.badge_text.configure(
                text=f"{self.action_a_text} (≤ {self.threshold}%)",
                text_color="#10b981"
            )
            self.roll_label.configure(text_color="#10b981")
        else:
            self.badge_frame.configure(fg_color="#1e293b", border_color="#334155")
            self.badge_text.configure(
                text=f"{self.action_b_text} (> {self.threshold}%)",
                text_color="#94a3b8"
            )
            self.roll_label.configure(text_color="#f8fafc")

    def adjust_threshold(self, delta):
        self.set_threshold(self.threshold + delta)

    # -------------------------------------------------------------------------
    # Controls (Topmost, Mute, Auto)
    # -------------------------------------------------------------------------
    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        self.attributes("-topmost", self.is_topmost)
        self.pin_btn.configure(
            fg_color="#10b981" if self.is_topmost else "#1e293b",
            text_color="#ffffff" if self.is_topmost else "#64748b"
        )

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.sound_btn.configure(
            text="🔇" if self.is_muted else "🔊",
            text_color="#ef4444" if self.is_muted else "#94a3b8"
        )

    def on_mode_change(self, mode_str):
        if mode_str == "Manuelt":
            self.stop_auto_roll()
        elif "1s" in mode_str:
            self.start_auto_roll(1.0)
        elif "2s" in mode_str:
            self.start_auto_roll(2.0)
        elif "3s" in mode_str:
            self.start_auto_roll(3.0)

    def toggle_auto_roll(self):
        if self.is_auto:
            self.mode_seg.set("Manuelt")
            self.stop_auto_roll()
        else:
            self.mode_seg.set("Auto 2s")
            self.start_auto_roll(2.0)

    def start_auto_roll(self, interval):
        self.is_auto = True
        self.auto_interval_sec = interval
        self._auto_thread_running = True

        def auto_worker():
            while self._auto_thread_running and self.is_auto:
                time.sleep(self.auto_interval_sec)
                if not self._auto_thread_running or not self.is_auto:
                    break
                # Safely invoke on main thread
                try:
                    self.after(0, self.execute_roll)
                except Exception:
                    break

        threading.Thread(target=auto_worker, daemon=True).start()

    def stop_auto_roll(self):
        self.is_auto = False
        self._auto_thread_running = False

    def on_closing(self):
        self.stop_auto_roll()
        self.destroy()


if __name__ == "__main__":
    app = PokerRNGApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
