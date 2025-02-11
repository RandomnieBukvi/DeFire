import socket


class WifiCarManager:
    broadcast_port = 1235
    buffer_size = 1024
    broadcast_name = 'car'
    device_ip = None
    udp_socket = None

    @staticmethod
    def initialize_socket():
        """Инициализация UDP-сокета только один раз"""
        if WifiCarManager.udp_socket is None:
            WifiCarManager.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            WifiCarManager.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            WifiCarManager.udp_socket.bind(("0.0.0.0", WifiCarManager.broadcast_port))
            print("CAR: UDP-сокет инициализирован")
        else:
            print("CAR: UDP-сокет УЖЕ инициализирован")

    @staticmethod
    def receive_broadcast():
        WifiCarManager.initialize_socket()  # Инициализируем сокет, если еще не инициализирован

        print("CAR: Ожидание broadcast-сообщений...")
        while True:
            message, addr = WifiCarManager.udp_socket.recvfrom(WifiCarManager.buffer_size)  # Ждем данные (до 1024 байт)
            print(f"CAR: Получено сообщение: {message.decode()} от {addr}")
            if message.decode() == WifiCarManager.broadcast_name:
                WifiCarManager.device_ip = addr[0]
                break

    @staticmethod
    def send_data(message):
        if WifiCarManager.device_ip is None:
            print("CAR: IP-адрес устройства не определен. Сначала выполните получение broadcast-сообщения.")
            return
        # Отправляем данные на сохраненный IP-адрес
        WifiCarManager.udp_socket.sendto(message.encode(), (WifiCarManager.device_ip, WifiCarManager.broadcast_port))
        # print(f"Отправлено сообщение: {message} на {WiFiTaskManager.device_ip}")

    @staticmethod
    def close_socket():
        if WifiCarManager.udp_socket is not None:
            WifiCarManager.udp_socket.close()
            WifiCarManager.udp_socket = None
            print("CAR: UDP-сокет закрыт")
#
# from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QMouseEvent, QCursor
#
# class GameWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.max_delta_x = 100
#         self.max_delta_y = 100
#
#         self.setWindowTitle("Mouse Tracking Example")
#         self.setGeometry(100, 100, 800, 600)
#
#         # Центр окна
#         self.center = self.rect().center()
#
#         self.tracking_enabled = False
#         self.setMouseTracking(False)
#
#         self.label = QLabel(self)
#         self.label.setGeometry(10, 10, 200, 40)  # Позиция и размер текста
#         self.label.setText("Mouse tracking disabled")
#
#     def mouseMoveEvent(self, event: QMouseEvent):
#         if not self.tracking_enabled:
#             return
#         # Получаем текущие координаты мыши
#         current_pos = event.pos()
#
#         # Вычисляем смещение мыши от центра
#         delta_x = current_pos.x() - self.center.x()
#         delta_y = current_pos.y() - self.center.y()
#
#         delta_x = max(-1 * self.max_delta_x, min(self.max_delta_x, delta_x))
#         delta_y = max(-1 * self.max_delta_y, min(self.max_delta_y, delta_y))
#         # Здесь можно использовать смещение (delta_x, delta_y)
#         mouse_status = f"Mouse delta: {delta_x}, {delta_y}"
#         # print(mouse_status)
#         # Если ЛКМ нажата, добавляем соответствующее сообщение
#         if self.left_click_pressed:
#             mouse_status += " | Left button pressed"
#
#         self.label.setText(mouse_status)
#         # для управления камерой или объектами
#         # self.label.setText(f"Mouse delta: {delta_x}, {delta_y}")
#         # Возвращаем курсор в центр окна
#         QCursor.setPos(self.mapToGlobal(self.center))
#
#     def keyPressEvent(self, event):
#         # Проверяем, нажата ли клавиша Escape
#         if event.key() == Qt.Key_Escape:
#             # Отключаем отслеживание мыши
#             self.setMouseTracking(False)
#             self.tracking_enabled = False
#             self.setCursor(Qt.ArrowCursor)  # Возвращаем видимость курсора
#             self.label.setText("Mouse tracking disabled")
#         elif event.key() == Qt.Key_Space:
#             # Включаем отслеживание мыши
#             self.setMouseTracking(True)
#             self.tracking_enabled = True
#             self.setCursor(Qt.BlankCursor)  # Скрываем курсор снова
#
#     def mousePressEvent(self, event: QMouseEvent):
#         if event.button() == Qt.LeftButton:
#             # Отслеживаем нажатие ЛКМ
#             self.left_click_pressed = True
#             self.label.setText(self.label.text() + " | Left button pressed")
#
#     def mouseReleaseEvent(self, event: QMouseEvent):
#         if event.button() == Qt.LeftButton:
#             # Отслеживаем отпускание ЛКМ
#             self.left_click_pressed = False
#             self.label.setText(self.label.text().replace(" | Left button pressed", ""))

# if __name__ == "__main__":
#     app = QApplication([])
#     window = GameWindow()
#     window.show()
#     sys.exit(app.exec())


# commands_dict = {
#     'w': 'forward',
#     's': 'backward',
#     'a': 'left',
#     'd': 'right'
# }

# if __name__ == '__main__':
#     WifiCarManager.receive_broadcast()
#     while True:
#         a = input()
#         if a == 'stop plz':
#             break
#         else:
#             command = commands_dict.get(a, 'stop')
#             WifiCarManager.send_data(command)
