#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerLab RNG - a small random number generator (1-100) for GTO mixed frequencies.
Built with PyQt6 for a smooth window that can be dragged between monitors,
cryptographic random numbers, and single-trigger Hover Mode.
"""

import sys
import os
import secrets
import threading
import time

# Set Windows App ID so taskbar displays the custom icon properly
try:
    import ctypes
    myappid = 'neslo.pokerlab.rng.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QFrame
)
from PyQt6.QtGui import QFont, QColor, QPalette, QKeyEvent, QIcon, QPixmap

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller onefile package."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(base_path, relative_path)
    if os.path.exists(target):
        return target
    local_target = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    return local_target


def async_beep(freq, duration_ms):
    """Play a short beep asynchronously to avoid any UI thread blocking."""
    if not HAS_WINSOUND:
        return
    def _run():
        try:
            winsound.Beep(freq, duration_ms)
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()


class HoverCard(QFrame):
    """
    Interactive card widget.
    Guarantees EXACTLY ONE roll per cursor sweep across the card.
    """
    clicked = pyqtSignal()
    hover_triggered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hover_enabled = False
        self.mouse_inside = False
        self.last_hover_time = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.hover_enabled and not self.mouse_inside:
            self.mouse_inside = True
            now = time.time()
            # Enforce at least 0.30s cooldown between distinct sweeps
            if now - self.last_hover_time > 0.30:
                self.last_hover_time = now
                self.hover_triggered.emit()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.mouse_inside = False


class PokerRNGQtApp(QWidget):
    def __init__(self):
        super().__init__()

        # 1. Fixed Window Size & Properties (Zero resize lag, compact footprint)
        self.setFixedSize(240, 420)
        self.setWindowTitle("PokerLab RNG")
        
        # Set Window & App Icon
        self.icon_path = get_resource_path("icon.png")
        if os.path.exists(self.icon_path):
            app_icon = QIcon(self.icon_path)
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)

        # Always on Top by default for poker multi-tabling
        self.is_topmost = True
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # 2. Core State
        self.min_val = 1
        self.max_val = 100
        self.threshold = 50
        self.current_roll = 50
        self.action_a_text = "BET / RAISE"
        self.action_b_text = "CHECK / FOLD"

        self.is_muted = False
        self.mode = "manual"  # 'manual' | 'hover' | 'auto_1s' | 'auto_2s' | 'auto_3s'
        self.auto_interval_ms = 2000

        self.history = []  # List of tuples: (number, is_action_a)
        self.total_rolls = 0
        self.sum_rolls = 0

        # Auto-roll Timer
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.execute_roll)

        # 3. Setup UI & Styling
        self.apply_dark_theme()
        self.build_ui()

        # Initial Roll
        self.execute_roll(play_sound=False)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #080c14;
                color: #f8fafc;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }
            QFrame#mainCard {
                background-color: #0e1524;
                border: 1px solid #1c283f;
                border-radius: 12px;
            }
            QFrame#mainCard:hover {
                border: 1px solid #2e4166;
            }
            QLabel#rollLabel {
                font-family: 'Consolas', monospace;
                font-size: 52px;
                font-weight: bold;
                color: #f8fafc;
            }
            QLabel#badgeLabel {
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            }
            QPushButton#btnRoll {
                background-color: #10b981;
                color: #022c22;
                font-size: 13px;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px;
                border: none;
            }
            QPushButton#btnRoll:hover {
                background-color: #059669;
            }
            QPushButton#btnRoll:pressed {
                background-color: #047857;
            }
            QPushButton.modeBtn {
                background-color: #111a2c;
                color: #94a3b8;
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #1e2d48;
                border-radius: 6px;
                padding: 4px;
            }
            QPushButton.modeBtn:hover {
                color: #f8fafc;
                border-color: #334b75;
            }
            QPushButton.modeBtn.active {
                background-color: #1a2740;
                color: #10b981;
                border: 1px solid #10b981;
            }
            QPushButton.presetBtn {
                background-color: #0e1626;
                color: #94a3b8;
                font-family: 'Consolas', monospace;
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #1c283e;
                border-radius: 4px;
                padding: 3px;
            }
            QPushButton.presetBtn:hover {
                color: #10b981;
                border-color: #10b981;
            }
            QPushButton.presetBtn.active {
                background-color: #10b981;
                color: #022c22;
                border-color: #10b981;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #192338;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #10b981;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #10b981;
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }
        """)

    def build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 8, 10, 8)
        root_layout.setSpacing(6)

        # -------------------------------------------------------------
        # 1. Top Bar: Brand Icon, App Title, Pin, Sound
        # -------------------------------------------------------------
        top_bar = QHBoxLayout()
        top_bar.setSpacing(6)

        # Brand Icon inside the program
        self.brand_icon = QLabel()
        self.brand_icon.setFixedSize(20, 20)
        self.brand_icon.setScaledContents(True)
        if os.path.exists(self.icon_path):
            self.brand_icon.setPixmap(QPixmap(self.icon_path))
        top_bar.addWidget(self.brand_icon)

        self.title_label = QLabel("POKERLAB RNG")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #10b981; letter-spacing: 1.2px;")
        top_bar.addWidget(self.title_label)

        top_bar.addStretch()

        # Sound Button
        self.sound_btn = QPushButton("🔊")
        self.sound_btn.setFixedSize(26, 24)
        self.sound_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sound_btn.setToolTip("Toggle Sound (M)")
        self.sound_btn.setStyleSheet("background-color: #111a2c; border: 1px solid #1e2d48; border-radius: 5px; font-size: 11px;")
        self.sound_btn.clicked.connect(self.toggle_mute)
        top_bar.addWidget(self.sound_btn)

        # Pin / Always on Top Button
        self.pin_btn = QPushButton("📌")
        self.pin_btn.setFixedSize(26, 24)
        self.pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_btn.setToolTip("Toggle Always On Top (T)")
        self.pin_btn.setStyleSheet("background-color: #10b981; color: white; border: none; border-radius: 5px; font-size: 11px;")
        self.pin_btn.clicked.connect(self.toggle_topmost)
        top_bar.addWidget(self.pin_btn)

        root_layout.addLayout(top_bar)

        # -------------------------------------------------------------
        # 2. Main Number Card (Clickable & Single-Trigger Hover Mode)
        # -------------------------------------------------------------
        self.card = HoverCard()
        self.card.setObjectName("mainCard")
        self.card.clicked.connect(self.execute_roll)
        self.card.hover_triggered.connect(self.execute_roll)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(8, 6, 8, 8)
        card_layout.setSpacing(2)

        self.roll_label = QLabel("50")
        self.roll_label.setObjectName("rollLabel")
        self.roll_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Make child label transparent to mouse events so card is one solid hitbox
        self.roll_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        card_layout.addWidget(self.roll_label)

        # Decision Badge
        self.badge_label = QLabel("BET / RAISE  (≤ 50%)")
        self.badge_label.setObjectName("badgeLabel")
        self.badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Make child badge transparent to mouse events as well
        self.badge_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        card_layout.addWidget(self.badge_label)

        root_layout.addWidget(self.card)

        # -------------------------------------------------------------
        # 3. Main Roll Button
        # -------------------------------------------------------------
        self.btn_roll = QPushButton("ROLL RNG (Space)")
        self.btn_roll.setObjectName("btnRoll")
        self.btn_roll.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_roll.clicked.connect(self.execute_roll)
        root_layout.addWidget(self.btn_roll)

        # -------------------------------------------------------------
        # 4. Mode Buttons: [Manual] [Hover] [Auto 2s] [Auto 1s]
        # -------------------------------------------------------------
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(4)

        self.btn_mode_manual = QPushButton("Manual")
        self.btn_mode_manual.setProperty("class", "modeBtn")
        self.btn_mode_manual.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_manual.clicked.connect(lambda: self.set_mode("manual"))
        mode_layout.addWidget(self.btn_mode_manual)

        self.btn_mode_hover = QPushButton("Hover")
        self.btn_mode_hover.setProperty("class", "modeBtn")
        self.btn_mode_hover.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_hover.setToolTip("Rolls automatically when cursor sweeps across the card")
        self.btn_mode_hover.clicked.connect(lambda: self.set_mode("hover"))
        mode_layout.addWidget(self.btn_mode_hover)

        self.btn_mode_auto2 = QPushButton("Auto 2s")
        self.btn_mode_auto2.setProperty("class", "modeBtn")
        self.btn_mode_auto2.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_auto2.clicked.connect(lambda: self.set_mode("auto_2s"))
        mode_layout.addWidget(self.btn_mode_auto2)

        self.btn_mode_auto1 = QPushButton("Auto 1s")
        self.btn_mode_auto1.setProperty("class", "modeBtn")
        self.btn_mode_auto1.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_auto1.clicked.connect(lambda: self.set_mode("auto_1s"))
        mode_layout.addWidget(self.btn_mode_auto1)

        root_layout.addLayout(mode_layout)

        # -------------------------------------------------------------
        # 5. GTO Frequency Threshold & Presets
        # -------------------------------------------------------------
        freq_header = QHBoxLayout()
        freq_title = QLabel("Threshold:")
        freq_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b;")
        freq_header.addWidget(freq_title)

        freq_header.addStretch()

        self.freq_val_label = QLabel("50%")
        self.freq_val_label.setStyleSheet("font-family: 'Consolas', monospace; font-size: 11px; font-weight: bold; color: #10b981;")
        freq_header.addWidget(self.freq_val_label)
        root_layout.addLayout(freq_header)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(self.threshold)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider.valueChanged.connect(self.on_slider_changed)
        root_layout.addWidget(self.slider)

        # Quick Preset Buttons: 25%, 33%, 50%, 75%
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(4)
        self.preset_buttons = {}
        for p in [25, 33, 50, 75]:
            btn = QPushButton(f"{p}%")
            btn.setProperty("class", "presetBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, val=p: self.set_threshold(val))
            presets_layout.addWidget(btn)
            self.preset_buttons[p] = btn
        root_layout.addLayout(presets_layout)

        # -------------------------------------------------------------
        # 6. Mini History Strip
        # -------------------------------------------------------------
        self.history_layout = QHBoxLayout()
        self.history_layout.setSpacing(3)
        self.history_widgets = []
        for _ in range(6):
            lbl = QLabel("—")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("""
                font-family: 'Consolas', monospace;
                font-size: 10px;
                font-weight: bold;
                background-color: #0e1626;
                color: #64748b;
                border-radius: 4px;
                padding: 3px 0;
            """)
            self.history_layout.addWidget(lbl)
            self.history_widgets.append(lbl)
        root_layout.addLayout(self.history_layout)

        # -------------------------------------------------------------
        # 7. Stats Footer
        # -------------------------------------------------------------
        self.stats_label = QLabel("Rolls: 0 | Avg: —")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setStyleSheet("font-family: 'Consolas', monospace; font-size: 9px; color: #475569; padding-top: 2px;")
        root_layout.addWidget(self.stats_label)

        # Set default active mode button
        self.update_mode_ui()
        self.update_preset_ui()

    # -----------------------------------------------------------------
    # Core Roll Engine
    # -----------------------------------------------------------------
    def execute_roll(self, play_sound=True):
        # Unbiased, uniform random integer using secrets (CSPRNG)
        val = secrets.randbelow(self.max_val - self.min_val + 1) + self.min_val
        self.current_roll = val
        is_action_a = val <= self.threshold

        # Update Number
        self.roll_label.setText(f"{val:02d}" if val < 10 else str(val))

        # Update Badge and Colors
        if is_action_a:
            self.roll_label.setStyleSheet("font-family: 'Consolas', monospace; font-size: 52px; font-weight: bold; color: #10b981;")
            self.badge_label.setText(f"{self.action_a_text} (≤ {self.threshold}%)")
            self.badge_label.setStyleSheet("""
                background-color: #064e3b;
                color: #10b981;
                border: 1px solid #10b981;
                font-size: 10px;
                font-weight: bold;
                padding: 3px 6px;
                border-radius: 5px;
            """)
        else:
            self.roll_label.setStyleSheet("font-family: 'Consolas', monospace; font-size: 52px; font-weight: bold; color: #f8fafc;")
            self.badge_label.setText(f"{self.action_b_text} (> {self.threshold}%)")
            self.badge_label.setStyleSheet("""
                background-color: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                font-size: 10px;
                font-weight: bold;
                padding: 3px 6px;
                border-radius: 5px;
            """)

        # Sound
        if play_sound and not self.is_muted:
            freq = 880 if is_action_a else 440
            async_beep(freq, 35)

        # History & Stats
        self.total_rolls += 1
        self.sum_rolls += val
        self.history.insert(0, (val, is_action_a))
        if len(self.history) > 6:
            self.history.pop()

        self.update_history_ui()
        self.update_stats_ui()

    def update_history_ui(self):
        for i, lbl in enumerate(self.history_widgets):
            if i < len(self.history):
                num, is_a = self.history[i]
                txt = f"{num:02d}" if num < 10 else str(num)
                lbl.setText(txt)
                if is_a:
                    lbl.setStyleSheet("font-family: 'Consolas', monospace; font-size: 10px; font-weight: bold; background-color: #064e3b; color: #10b981; border-radius: 4px; padding: 3px 0;")
                else:
                    lbl.setStyleSheet("font-family: 'Consolas', monospace; font-size: 10px; font-weight: bold; background-color: #182234; color: #94a3b8; border-radius: 4px; padding: 3px 0;")
            else:
                lbl.setText("—")
                lbl.setStyleSheet("font-family: 'Consolas', monospace; font-size: 10px; font-weight: bold; background-color: #0e1626; color: #64748b; border-radius: 4px; padding: 3px 0;")

    def update_stats_ui(self):
        if self.total_rolls > 0:
            avg = self.sum_rolls / self.total_rolls
            self.stats_label.setText(f"Rolls: {self.total_rolls} | Avg: {avg:.1f}")

    # -----------------------------------------------------------------
    # Threshold Management
    # -----------------------------------------------------------------
    def on_slider_changed(self, value):
        self.set_threshold(value)

    def set_threshold(self, value):
        self.threshold = max(0, min(100, int(value)))
        self.slider.blockSignals(True)
        self.slider.setValue(self.threshold)
        self.slider.blockSignals(False)

        self.freq_val_label.setText(f"{self.threshold}%")
        self.update_preset_ui()

        # Re-evaluate current roll against new threshold
        is_action_a = self.current_roll <= self.threshold
        if is_action_a:
            self.roll_label.setStyleSheet("font-family: 'Consolas', monospace; font-size: 52px; font-weight: bold; color: #10b981;")
            self.badge_label.setText(f"{self.action_a_text} (≤ {self.threshold}%)")
            self.badge_label.setStyleSheet("background-color: #064e3b; color: #10b981; border: 1px solid #10b981; font-size: 10px; font-weight: bold; padding: 3px 6px; border-radius: 5px;")
        else:
            self.roll_label.setStyleSheet("font-family: 'Consolas', monospace; font-size: 52px; font-weight: bold; color: #f8fafc;")
            self.badge_label.setText(f"{self.action_b_text} (> {self.threshold}%)")
            self.badge_label.setStyleSheet("background-color: #1e293b; color: #94a3b8; border: 1px solid #334155; font-size: 10px; font-weight: bold; padding: 3px 6px; border-radius: 5px;")

    def update_preset_ui(self):
        for p, btn in self.preset_buttons.items():
            if p == self.threshold:
                btn.setStyleSheet("background-color: #10b981; color: #022c22; font-family: 'Consolas', monospace; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 3px; border: none;")
            else:
                btn.setStyleSheet("background-color: #0e1626; color: #94a3b8; font-family: 'Consolas', monospace; font-size: 10px; font-weight: bold; border: 1px solid #1c283e; border-radius: 4px; padding: 3px;")

    # -----------------------------------------------------------------
    # Modes (Manual, Hover, Auto)
    # -----------------------------------------------------------------
    def set_mode(self, mode_name):
        self.mode = mode_name
        self.auto_timer.stop()
        self.card.hover_enabled = (mode_name == "hover")
        self.card.mouse_inside = False

        if mode_name == "auto_1s":
            self.auto_timer.start(1000)
        elif mode_name == "auto_2s":
            self.auto_timer.start(2000)
        elif mode_name == "auto_3s":
            self.auto_timer.start(3000)

        self.update_mode_ui()

    def update_mode_ui(self):
        buttons = {
            "manual": self.btn_mode_manual,
            "hover": self.btn_mode_hover,
            "auto_2s": self.btn_mode_auto2,
            "auto_1s": self.btn_mode_auto1
        }
        for name, btn in buttons.items():
            if name == self.mode:
                btn.setStyleSheet("background-color: #1a2740; color: #10b981; font-size: 10px; font-weight: bold; border: 1px solid #10b981; border-radius: 6px; padding: 4px;")
            else:
                btn.setStyleSheet("background-color: #111a2c; color: #94a3b8; font-size: 10px; font-weight: bold; border: 1px solid #1e2d48; border-radius: 6px; padding: 4px;")

    # -----------------------------------------------------------------
    # Controls (Topmost Pin, Mute)
    # -----------------------------------------------------------------
    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        if self.is_topmost:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.pin_btn.setStyleSheet("background-color: #10b981; color: white; border: none; border-radius: 5px; font-size: 11px;")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.pin_btn.setStyleSheet("background-color: #111a2c; color: #64748b; border: 1px solid #1e2d48; border-radius: 5px; font-size: 11px;")
        self.show()

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.sound_btn.setText("🔇")
            self.sound_btn.setStyleSheet("background-color: #111a2c; color: #ef4444; border: 1px solid #ef4444; border-radius: 5px; font-size: 11px;")
        else:
            self.sound_btn.setText("🔊")
            self.sound_btn.setStyleSheet("background-color: #111a2c; color: #f8fafc; border: 1px solid #1e2d48; border-radius: 5px; font-size: 11px;")
            async_beep(700, 30)

    # -----------------------------------------------------------------
    # Keyboard Shortcuts
    # -----------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_Space:
            self.execute_roll()
            event.accept()
        elif key == Qt.Key.Key_H:
            self.set_mode("manual" if self.mode == "hover" else "hover")
            event.accept()
        elif key == Qt.Key.Key_A:
            self.set_mode("manual" if "auto" in self.mode else "auto_2s")
            event.accept()
        elif key == Qt.Key.Key_T:
            self.toggle_topmost()
            event.accept()
        elif key == Qt.Key.Key_M:
            self.toggle_mute()
            event.accept()
        elif key == Qt.Key.Key_Up:
            self.set_threshold(self.threshold + 5)
            event.accept()
        elif key == Qt.Key.Key_Down:
            self.set_threshold(self.threshold - 5)
            event.accept()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    window = PokerRNGQtApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
