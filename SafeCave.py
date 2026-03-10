import sys
import os
import datetime
import requests
import webbrowser
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QImage, QPixmap, QTransform
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame)

# --- CONFIG & BRANDING ---
PHONE_IPS = ["192.168.1.109", "192.168.1.241"]
WIDTH, HEIGHT = 540, 400 
SNAP_DIR = "SafeCave Snap Shots"

if not os.path.exists(SNAP_DIR):
    os.makedirs(SNAP_DIR)

# CavemanAI Branding Palette
C_STONE = "#1e1e2e"
C_PURPLE = "#6c5ce7"
C_MINT = "#55e6c1"
C_TEXT = "#dfe6e9"

class SafeCaveStreamWorker(QThread):
    """Surgical MJPEG handler designed to eliminate 'Two SOI' terminal errors."""
    frame_ready = Signal(QImage)
    status_signal = Signal(bool)

    def __init__(self, ip):
        super().__init__()
        self.url = f"http://{ip}:8080/video"
        self.running = True
        self.last_raw_image = None
        self.session = requests.Session()

    def run(self):
        while self.running:
            try:
                # stream=True is vital for handling high-frequency MJPEG data
                response = self.session.get(self.url, stream=True, timeout=5)
                if response.status_code == 200:
                    self.status_signal.emit(True)
                    raw_buffer = bytes()
                    
                    for chunk in response.iter_content(chunk_size=32768):
                        if not self.running: break
                        raw_buffer += chunk
                        
                        # Locate the start and end of the JPEG strictly
                        start = raw_buffer.find(b'\xff\xd8')
                        end = raw_buffer.find(b'\xff\xd9', start)
                        
                        if start != -1 and end != -1:
                            # Extract exactly one frame
                            jpg_data = raw_buffer[start:end+2]
                            # Immediately dump the buffer to ensure the next search starts fresh
                            raw_buffer = raw_buffer[end+2:]
                            
                            img = QImage.fromData(jpg_data)
                            if not img.isNull():
                                if img.width() < img.height():
                                    img = img.transformed(QTransform().rotate(90))
                                
                                self.last_raw_image = img.copy()
                                self.frame_ready.emit(img)
                            
                        # If buffer gets messy/large without a valid frame, reset it
                        if len(raw_buffer) > 1000000: raw_buffer = bytes()
                else:
                    self.status_signal.emit(False)
            except Exception:
                self.status_signal.emit(False)
                self.msleep(2000)

class CameraUnit(QFrame):
    def __init__(self, ip, name):
        super().__init__()
        self.name = name
        self.setStyleSheet(f"QFrame {{ background-color: #000; border: 3px solid {C_STONE}; border-radius: 10px; }}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2,2,2,2)
        
        self.header = QFrame()
        self.header.setFixedHeight(25)
        self.header.setStyleSheet(f"background-color: {C_STONE}; border-top-left-radius: 7px; border-top-right-radius: 7px;")
        h_lay = QHBoxLayout(self.header)
        h_lay.setContentsMargins(10,0,10,0)
        
        self.dot = QLabel("●")
        self.dot.setStyleSheet("color: #ff7675; font-size: 12px; border: none;")
        self.id_lbl = QLabel(name)
        self.id_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 10px; font-weight: bold; font-family: 'Verdana';")
        h_lay.addWidget(self.dot); h_lay.addWidget(self.id_lbl); h_lay.addStretch()
        
        self.feed = QLabel("ACQUIRING...", alignment=Qt.AlignCenter)
        self.feed.setStyleSheet(f"color: {C_PURPLE}; border: none;")
        self.feed.setMinimumSize(QSize(WIDTH, HEIGHT))
        layout.addWidget(self.header); layout.addWidget(self.feed)

        self.worker = SafeCaveStreamWorker(ip)
        self.worker.frame_ready.connect(self.update_ui)
        self.worker.status_signal.connect(self.update_status)
        self.worker.start()

    def update_ui(self, img):
        pix = QPixmap.fromImage(img).scaled(self.feed.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.feed.setPixmap(pix)

    def update_status(self, online):
        self.dot.setStyleSheet(f"color: {C_MINT if online else '#ff7675'}; font-size: 12px; border: none;")

    def save_snapshot(self):
        if self.worker.last_raw_image:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(SNAP_DIR, f"CAVE_{self.name.replace(' ','_')}_{timestamp}.jpg")
            self.worker.last_raw_image.save(filename, "JPG")
            return filename
        return None

class SafeCaveMothership(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CavemanAI | SafeCave Monitor")
        self.setStyleSheet("background-color: #0f0f1a;") 
        self.showMaximized()
        central = QWidget()
        self.setCentralWidget(central)
        self.grid = QGridLayout(central)
        self.grid.setSpacing(10)
        self.units = []
        for i, ip in enumerate(PHONE_IPS):
            row, col = divmod(i, 3)
            unit = CameraUnit(ip, f"CAVE-EYE {i+1:02d}")
            self.grid.addWidget(unit, row, col)
            self.units.append(unit)

    def closeEvent(self, event):
        for unit in self.units:
            unit.worker.running = False
            unit.worker.quit()
        event.accept()

class SafeCaveController(QWidget):
    def __init__(self, camera_units):
        super().__init__()
        self.camera_units = camera_units
        self.setWindowTitle("SafeCave Command Center")
        self.setFixedSize(400, 350)
        self.setStyleSheet(f"background-color: {C_STONE}; border: 2px solid {C_PURPLE};")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        main_lay = QVBoxLayout(self)
        
        # Header
        header_lay = QHBoxLayout()
        self.logo_lbl = QLabel()
        logo_img = QPixmap("SafeCave.jpeg") 
        if not logo_img.isNull():
            self.logo_lbl.setPixmap(logo_img.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_lay.addWidget(self.logo_lbl)
        
        self.hub_title = QLabel("SafeCave\nCommand Center")
        self.hub_title.setStyleSheet(f"color: {C_MINT}; font-size: 20px; font-weight: bold; border: none;")
        header_lay.addWidget(self.hub_title)
        header_lay.addStretch()
        main_lay.addLayout(header_lay)

        # Single Action Button
        self.btn_snap = QPushButton("SNAPSHOT CAVE EYES")
        self.btn_snap.setCursor(Qt.PointingHandCursor)
        self.btn_snap.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_PURPLE};
                color: white;
                font-weight: bold;
                padding: 20px;
                border-radius: 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {C_MINT};
                color: {C_STONE};
            }}
        """)
        self.btn_snap.clicked.connect(self.take_all_snapshots)
        
        main_lay.addSpacing(30)
        main_lay.addWidget(self.btn_snap)
        main_lay.addStretch()

    def take_all_snapshots(self):
        for u in self.camera_units: u.save_snapshot()
        print("CavemanAI: All Eyes Captured.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = SafeCaveMothership()
    monitor.show()
    controller = SafeCaveController(monitor.units)
    controller.show()
    sys.exit(app.exec())
