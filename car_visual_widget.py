# gui/car_visual_widget.py
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QPainter, QColor

# Map CAN IDs to physical systems
ID_TO_SYSTEM = {
    0x0C5: "engine",      # Engine RPM / Powertrain
    0x0B0: "brakes",       # Brake System
    0x0B4: "engine",
    0x0D0: "brakes",
    0x000: "engine",       # DoS affects all
}

class CarDiagramWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.attacked_system = None
        self.setMinimumSize(500, 300)
        
    @pyqtSlot(int)
    def highlight_attack(self, can_id):
        system = ID_TO_SYSTEM.get(can_id, None)
        if can_id == 0x000:
            system = "all" # DoS
            
        self.attacked_system = system
        self.update() # Trigger repaint
        print(f"[UI] Highlighting: {system}")

    def clear_highlight(self):
        self.attacked_system = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw simple car top-view
        painter.setBrush(QColor("#2C3E50"))
        painter.drawRoundedRect(150, 50, 200, 250, 20, 20) # Car body

        # Default colors
        engine_color = QColor("#E74C3C") if self.attacked_system in ["engine", "all"] else QColor("#95A5A6")
        brakes_color = QColor("#E74C3C") if self.attacked_system in ["brakes", "all"] else QColor("#95A5A6")

        # Engine (Front)
        painter.setBrush(engine_color)
        painter.drawRect(170, 60, 160, 60)
        painter.drawText(210, 95, "ENGINE")

        # Brakes (Wheels)
        painter.setBrush(brakes_color)
        painter.drawRect(130, 80, 30, 50)   # FL
        painter.drawRect(340, 80, 30, 50)   # FR
        painter.drawRect(130, 220, 30, 50)  # RL
        painter.drawRect(340, 220, 30, 50)  # RR
        painter.drawText(185, 250, "BRAKES")

        # Status Text
        if self.attacked_system:
            painter.setPen(QColor("red"))
            painter.drawText(10, 20, f"ATTACK DETECTED: {self.attacked_system.upper()} UNDER ATTACK!")
