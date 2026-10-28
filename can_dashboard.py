"""
dashboard.py - CAN-Sentinel Week 3: Dashboard UI (PyQt)

A native desktop dashboard with:
  - A scrolling terminal-style view of raw CAN traffic
  - A "Threat Level" gauge that rises when alerts are detected

This demo version generates its own traffic via can_simulator's logic so
it runs standalone (no vcan0 needed to see the UI working). To wire it to
the REAL live feed instead, replace feed_one_frame()'s random generation
with lines read from realtime_detector.py's socket (see the comment in
feed_one_frame for exactly where to swap it in).

Needs:  pip install PyQt5
Run:    python3 dashboard.py
"""
import sys
import random
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QProgressBar
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPalette

from can_detector import detect_intrusion

ECU_IDS = {0x100: "Engine", 0x200: "Brake", 0x300: "Transmission", 0x400: "Steering"}


class CANSentinelDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN-Sentinel - Live Threat Dashboard")
        self.resize(760, 520)
        self.threat_level = 0  # 0-100, decays over time, spikes on alerts

        layout = QVBoxLayout()

        title = QLabel("CAN-Sentinel — Real-Time Intrusion Monitor")
        title.setFont(QFont("Consolas", 14, QFont.Bold))
        layout.addWidget(title)

        # --- Threat Level gauge ---
        gauge_row = QHBoxLayout()
        gauge_row.addWidget(QLabel("Threat Level:"))
        self.gauge = QProgressBar()
        self.gauge.setRange(0, 100)
        self.gauge.setValue(0)
        self.gauge.setTextVisible(True)
        gauge_row.addWidget(self.gauge)
        layout.addLayout(gauge_row)

        # --- Scrolling traffic view ---
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 10))
        self.log_view.setStyleSheet("background-color: #0c0c0c; color: #00ff66;")
        layout.addWidget(self.log_view)

        self.setLayout(layout)

        # Update loop: pulls one frame at a time (demo generator below)
        self.timer = QTimer()
        self.timer.timeout.connect(self.feed_one_frame)
        self.timer.start(300)  # ms between frames in this demo

    def feed_one_frame(self):
        # --- DEMO TRAFFIC GENERATOR ---
        # Swap this block for real frames from realtime_detector.py's
        # socket connection (see can_sniffer.c + realtime_detector.py)
        # to drive this dashboard off live vcan0 traffic instead.
        roll = random.random()
        if roll < 0.75:
            can_id = random.choice(list(ECU_IDS.keys()))
            dlc = 8
            data = [random.randint(0, 255) for _ in range(dlc)]
            if can_id == 0x100:
                rpm = random.randint(700, 6500)
                data = [(rpm >> 8) & 0xFF, rpm & 0xFF] + [0] * 6
        elif roll < 0.9:
            can_id = 0x100
            dlc = 8
            rpm = random.randint(20000, 60000)
            data = [(rpm >> 8) & 0xFF, rpm & 0xFF] + [0] * 6
        else:
            can_id = random.choice([0x000, 0x7FF, 0x123])
            dlc = random.randint(0, 8)
            data = [random.randint(0, 255) for _ in range(8)]
        # --- END DEMO GENERATOR ---

        result = detect_intrusion(can_id, dlc, data)
        ts = datetime.now().strftime("%H:%M:%S")
        ecu = ECU_IDS.get(can_id, "UNKNOWN")
        line = f"[{ts}] ID 0x{can_id:X} ({ecu}) DLC={dlc} | {result}"

        if "NORMAL" in result:
            self.log_view.append(f'<span style="color:#00ff66;">{line}</span>')
            self.threat_level = max(0, self.threat_level - 3)
        else:
            self.log_view.append(f'<span style="color:#ff4444;">{line}</span>')
            self.threat_level = min(100, self.threat_level + 25)

        self.gauge.setValue(self.threat_level)
        self._color_gauge()

    def _color_gauge(self):
        if self.threat_level < 30:
            color = "#2ecc71"   # green
        elif self.threat_level < 70:
            color = "#f1c40f"   # yellow
        else:
            color = "#e74c3c"   # red
        self.gauge.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; }}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CANSentinelDashboard()
    win.show()
    sys.exit(app.exec_())
