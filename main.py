from turret_manager import *
from wifi_manager import *
from gui2 import *

if __name__ == '__main__':
    WiFiTaskManager.receive_broadcast()
    TurretControl.initialize_model(model_path="../models_fire_detection_datasetv5/best2.pt")
    GUI.initialize()
    TurretControl.release_video_capture()
