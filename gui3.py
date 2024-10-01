from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import Qt
from turret_manager import TurretControl
from wifi_manager import WiFiTaskManager
import cv2
import numpy as np
from PIL import Image


class GUI(QWidget):
    control_status = None
    lbl_status = None
    btn_toggle = None
    lbl_video = None
    original_image = None

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Turret Control Interface")

        self.control_status = "Manual control: OFF"
        self.lbl_status = QLabel(self.control_status, self)

        self.btn_toggle = QPushButton("Toggle Control", self)
        self.btn_toggle.clicked.connect(self.toggle_control)

        self.lbl_video = QLabel(self)
        self.lbl_video.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.btn_toggle)
        layout.addWidget(self.lbl_video)
        self.setLayout(layout)

        self.show()
        self.update_frame()

    def keyPressEvent(self, event):
        if TurretControl.remote_control:
            dx, dy, shoot = 0, 0, 0
            if event.key() == Qt.Key_W:
                dy = 1
                print("Move turret forward")
            elif event.key() == Qt.Key_S:
                dy = -1
                print("Move turret backward")
            if event.key() == Qt.Key_A:
                dx = -1
                print("Move turret left")
            elif event.key() == Qt.Key_D:
                dx = 1
                print("Move turret right")
            if event.key() == Qt.Key_Space:
                shoot = 1
                print("Fire!")
            TurretControl.send_command(dx, dy, shoot)
        else:
            print("Manual control is off. No actions will be taken.")

    def toggle_control(self):
        TurretControl.remote_control = not TurretControl.remote_control
        TurretControl.is_shooting = False
        self.control_status = f"Manual control: {'ON' if TurretControl.remote_control else 'OFF'}"
        self.lbl_status.setText(self.control_status)
        print(f"Manual control {'enabled' if TurretControl.remote_control else 'disabled'}")

    def update_frame(self):
        img_resp = WiFiTaskManager.get_img_from_cam()
        if TurretControl.remote_control:
            imgnp = np.array(bytearray(img_resp.content), dtype=np.uint8)
            im = cv2.imdecode(imgnp, -1)
            sight_dimention = round(min(im.shape[0], im.shape[1]) * 0.1)
            sight_coordinates = [round((im.shape[1] - sight_dimention) / 2),
                                 round((im.shape[0] - sight_dimention) / 2),
                                 round((im.shape[1] - sight_dimention) / 2 + sight_dimention),
                                 round((im.shape[0] - sight_dimention) / 2 + sight_dimention)]
            im = cv2.rectangle(im, (sight_coordinates[0], sight_coordinates[1]),
                               (sight_coordinates[2], sight_coordinates[3]), (0, 255, 0), 5)
            im = cv2.rectangle(im,
                               (sight_coordinates[0] - sight_dimention, sight_coordinates[1] - sight_dimention),
                               (sight_coordinates[2] + sight_dimention, sight_coordinates[3] + sight_dimention),
                               (0, 255, 255), 5)
        else:
            im = TurretControl.recognize_fire(img_resp)

        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(im)
        img_qt = QPixmap.fromImage(QtGui.QImage(img.tobytes(), img.width, img.height, QtGui.QImage.Format_RGB888))

        self.lbl_video.setPixmap(img_qt)
        QtCore.QTimer.singleShot(10, self.update_frame)  # Обновление каждые 10 мс
