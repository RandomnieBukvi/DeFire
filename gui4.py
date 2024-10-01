import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer


class TurretControl(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.remote_control = False
        self.image_received = False

    def initUI(self):
        self.setWindowTitle('Turret Control')

        # Layout
        self.layout = QVBoxLayout()

        # Label to display the camera feed or placeholder text
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Button to toggle remote control mode
        self.control_button = QPushButton('Off', self)
        self.control_button.clicked.connect(self.toggle_control)
        self.layout.addWidget(self.control_button)

        # Label for control mode text
        self.control_mode_label = QLabel('Remote control', self)
        self.layout.addWidget(self.control_mode_label)

        self.setLayout(self.layout)

        # Set up timer for image update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(100)  # Update every 100 ms

        self.setGeometry(100, 100, 800, 600)

    def toggle_control(self):
        """Toggle between remote control and autonomous mode"""
        self.remote_control = not self.remote_control
        if self.remote_control:
            self.control_button.setText('On')
        else:
            self.control_button.setText('Off')

    def keyPressEvent(self, event):
        """Handle turret movement with keyboard when remote control is on"""
        if self.remote_control:
            if event.key() == Qt.Key_W:
                self.send_command('move_forward')
            elif event.key() == Qt.Key_A:
                self.send_command('move_left')
            elif event.key() == Qt.Key_S:
                self.send_command('move_backward')
            elif event.key() == Qt.Key_D:
                self.send_command('move_right')
            elif event.key() == Qt.Key_Space:
                self.send_command('fire')

    def send_command(self, command):
        """Send command to the turret (placeholder function)"""
        print(f'Sent command: {command}')

    def receive_image(self):
        """Receive image from the turret (placeholder function returning dummy image)"""
        # Replace this with actual camera image retrieval using OpenCV or other method
        self.image_received = True
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(dummy_image, 'Camera Feed', (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return dummy_image

    def update_image(self):
        """Update the displayed image"""
        image = self.receive_image()
        if self.image_received:
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
        else:
            self.image_label.setText("Waiting for camera feed...")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TurretControl()
    ex.show()
    sys.exit(app.exec_())
