import socket
import requests


class WiFiTaskManager:
    # Статические переменные
    broadcast_port = 1234
    buffer_size = 1024
    broadcast_name = 'DeFire'
    device_ip = None
    udp_socket = None

    @staticmethod
    def initialize_socket():
        """Инициализация UDP-сокета только один раз"""
        if WiFiTaskManager.udp_socket is None:
            WiFiTaskManager.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            WiFiTaskManager.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            WiFiTaskManager.udp_socket.bind(("0.0.0.0", WiFiTaskManager.broadcast_port))
            print("UDP-сокет инициализирован")
        else:
            print("UDP-сокет УЖЕ инициализирован")

    @staticmethod
    def receive_broadcast():
        WiFiTaskManager.initialize_socket()  # Инициализируем сокет, если еще не инициализирован

        print("Ожидание broadcast-сообщений...")
        while True:
            message, addr = WiFiTaskManager.udp_socket.recvfrom(WiFiTaskManager.buffer_size)  # Ждем данные (до 1024 байт)
            print(f"Получено сообщение: {message.decode()} от {addr}")
            if message.decode() == WiFiTaskManager.broadcast_name:
                WiFiTaskManager.device_ip = addr[0]
                break

    @staticmethod
    def send_data(message):
        if WiFiTaskManager.device_ip is None:
            print("IP-адрес устройства не определен. Сначала выполните получение broadcast-сообщения.")
            return

        # Отправляем данные на сохраненный IP-адрес
        WiFiTaskManager.udp_socket.sendto(message.encode(), (WiFiTaskManager.device_ip, WiFiTaskManager.broadcast_port))
        # print(f"Отправлено сообщение: {message} на {WiFiTaskManager.device_ip}")

    @staticmethod
    def close_socket():
        if WiFiTaskManager.udp_socket is not None:
            WiFiTaskManager.udp_socket.close()
            WiFiTaskManager.udp_socket = None
            print("UDP-сокет закрыт")

    @staticmethod
    def get_img_from_cam():
        try:
            img_responce = requests.get('http://' + WiFiTaskManager.device_ip + "/cam.jpg")
        except ConnectionError:
            print('Connection lost')
            return
        return img_responce

    @staticmethod
    def toggle_control():
        try:
            img_responce = requests.get('http://' + WiFiTaskManager.device_ip + "/toggle_control")
        except ConnectionError:
            print('Connection lost')
            return

# def get_turret_ip():
#     global broadcast_name
#     udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#     # Разрешаем повторное использование адреса (нужно для broadcast)
#     udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
#     # Привязываем сокет к IP и порту
#     udp_socket.bind(("0.0.0.0", 1234))
#
#     print("Ожидание broadcast-сообщений...")
#
#     # Получаем сообщение и адрес отправителя
#     while True:
#         message, addr = udp_socket.recvfrom(1024)  # Ждем данные (до 1024 байт)
#         print(f"Получено сообщение: {message.decode()} от {addr}")
#         if message.decode() == broadcast_name:
#             udp_socket.close()
#             return addr[0]  # Возвращаем IP-адрес отправителя
