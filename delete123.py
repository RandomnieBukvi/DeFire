from wifi_manager import *

if __name__ == "__main__":
    WiFiTaskManager.receive_broadcast()
    x = 90
    y = 90
    pump = 1

    WiFiTaskManager.send_data(f"!{x}@{y}#{pump};")
