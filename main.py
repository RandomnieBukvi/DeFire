from gui_pyqt5 import *
from car_manager import *
import sys

enable_car = False

if __name__ == '__main__':
    WiFiTaskManager.receive_broadcast()
    print(9)
    if enable_car:
        WifiCarManager.receive_broadcast()
        print(12)
    TurretControl.initialize_model(model_path="../models_fire_detection_datasetv5/best2.pt")
    print(14)
    # WiFiTaskManager.toggle_control()
    print(16)
    # GUI.initialize()
    App = QApplication(sys.argv)
    print(19)
    Root = MainWindow()
    print(21)
    Root.show()
    print(23)
    sys.exit(App.exec())