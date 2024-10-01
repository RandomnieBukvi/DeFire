import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from turret_manager import *
import cv2


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.VBL = QVBoxLayout()

        self.feed_label = QLabel()
        self.feed_label.setText('Loading camera...')
        self.feed_label.setAlignment(Qt.AlignCenter)
        self.feed_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.feed_label.setMinimumSize(320, 240)

        self.VBL.addWidget(self.feed_label)

        self.toggle_button = QPushButton("Manual control: OFF")
        self.toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toggle_button.setMaximumHeight(60)
        self.toggle_button.clicked.connect(self.toggle_control)
        self.toggle_button.setFocusPolicy(Qt.NoFocus)
        self.VBL.addWidget(self.toggle_button)

        self.imageManager = ImageManager()

        self.imageManager.start()
        self.imageManager.ImageUpdate.connect(self.image_update_slot)

        self.keyManager = KeyManager(self)
        self.keyManager.start()

        self.setLayout(self.VBL)

        self.pressed_keys = set()

    def image_update_slot(self, image):
        # Get the current size of the label to dynamically resize the image
        label_width = self.feed_label.width()
        label_height = self.feed_label.height()

        # Resize the image to fit the label while keeping the aspect ratio
        scaled_image = image.scaled(label_width, label_height, Qt.KeepAspectRatio)

        # Set the pixmap with the resized image
        self.feed_label.setPixmap(QPixmap.fromImage(scaled_image))
        # self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    # def cancel_feed(self):
    #     self.Worker1.stop()
    #     self.keyManager.stop()

    def closeEvent(self, event):
        self.imageManager.stop()  # Stop the worker thread
        self.keyManager.stop()
        TurretControl.release_video_capture()
        if TurretControl.remote_control:
            WiFiTaskManager.toggle_control()
        event.accept()  # Accept the close event

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return  # Ignore auto-repeat key events

        self.pressed_keys.add(event.key())
        # self.handleKeyPress()

    # Key release event handler
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return  # Ignore auto-repeat key events

        self.pressed_keys.discard(event.key())
        # self.handleKeyPress()

    def toggle_control(self):
        TurretControl.remote_control = not TurretControl.remote_control
        TurretControl.is_shooting = False
        # WiFiTaskManager.toggle_control()
        self.toggle_button.setText(f"Manual control: {'ON' if TurretControl.remote_control else 'OFF'}")
        print(f"Manual control {'enabled' if TurretControl.remote_control else 'disabled'}")


class ImageManager(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            img_resp = WiFiTaskManager.get_img_from_cam()
            # if img_resp.status_code != 200:
            #     print('IMAGE ERROR_______________')
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

            # im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            image = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            # flipped_image = cv2.flip(image, 1)
            flipped_image = image
            convert_to_qt_format = QImage(flipped_image.data, flipped_image.shape[1], flipped_image.shape[0],
                                          QImage.Format_RGB888)
            self.ImageUpdate.emit(convert_to_qt_format)

    def stop(self):
        self.ThreadActive = False
        self.quit()


class KeyManager(QThread):
    handleKeys = pyqtSignal(QImage)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            if TurretControl.remote_control:
                key_list = []
                dx, dy, shoot = 0, 0, 0
                if Qt.Key_W in self.main_window.pressed_keys:
                    key_list.append('W')
                    dy += 1
                if Qt.Key_S in self.main_window.pressed_keys:
                    key_list.append('S')
                    dy -= 1
                if Qt.Key_A in self.main_window.pressed_keys:
                    key_list.append('A')
                    dx += 1
                if Qt.Key_D in self.main_window.pressed_keys:
                    key_list.append('D')
                    dx -= 1
                if Qt.Key_Space in self.main_window.pressed_keys:
                    key_list.append('SPACE')
                    shoot = 1
                # if Qt.Key_Tab in self.main_window.pressed_keys:
                #     key_list.append('TAB')
                #     self.main_window.toggle_control()
                # print(key_list)
                TurretControl.send_command(dx, dy, shoot)
            time.sleep(0.1)


    def stop(self):
        self.ThreadActive = False
        self.quit()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())