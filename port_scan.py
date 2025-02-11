import serial.tools.list_ports


class PortScanner:
    @staticmethod
    def get_available_ports():
        # Получаем список всех доступных портов
        ports = serial.tools.list_ports.comports()
        available_ports = []
        for port, desc, hwid in sorted(ports):
            available_ports.append({"port": port, "description": desc, "hwid": hwid})
        return available_ports

    @staticmethod
    def find_arduino_port():
        # Получаем список портов и ищем среди них Arduino
        ports = PortScanner.get_available_ports()
        for port_info in ports:
            # Ищем характерные слова в описании устройства
            if "Arduino" in port_info['description'] or "CH340" in port_info['description']:
                return port_info['port']
        return None


# Пример использования
if __name__ == "__main__":
    arduino_port = PortScanner.find_arduino_port()
    if arduino_port:
        print(f"Arduino обнаружен на порту: {arduino_port}")
    else:
        print("Arduino не найден.")

# Пример использования
# if __name__ == "__main__":
#     available_ports = PortScanner.get_available_ports()
#     if available_ports:
#         print("Доступные COM-порты:")
#         for port_info in available_ports:
#             print(f"Порт: {port_info['port']}, Описание: {port_info['description']}, HWID: {port_info['hwid']}")
#     else:
#         print("COM-порты не найдены.")
