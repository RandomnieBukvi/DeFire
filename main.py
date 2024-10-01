from gui_pyqt5 import *
import sys

if __name__ == '__main__':
    WiFiTaskManager.receive_broadcast()
    TurretControl.initialize_model(model_path="../models_fire_detection_datasetv5/best2.pt")
    WiFiTaskManager.toggle_control()
    # GUI.initialize()
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())
