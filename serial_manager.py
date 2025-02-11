import serial
from port_scan import PortScanner

class SerialSender:
    serial_port = None  # Статическая переменная для хранения порта

    @staticmethod
    def open_port(port: str, baudrate: int = 9600):
        try:
            # Открываем последовательный порт один раз и сохраняем в статической переменной
            SerialSender.serial_port = serial.Serial(port, baudrate=baudrate)
            print(f"Порт {port} открыт.")
        except serial.SerialException as e:
            print(f"Ошибка при открытии порта: {e}")
            SerialSender.serial_port = None

    @staticmethod
    def send_data(data: str):
        if SerialSender.serial_port and SerialSender.serial_port.is_open:
            data += '\n'
            try:
                # Отправляем данные через открытый порт
                SerialSender.serial_port.write(data.encode())
                print(f"Данные '{data}' успешно отправлены.")
            except serial.SerialException as e:
                print(f"Ошибка при отправке данных: {e}")
        else:
            print("Порт закрыт или не открыт.")

    @staticmethod
    def close_port():
        if SerialSender.serial_port and SerialSender.serial_port.is_open:
            SerialSender.serial_port.close()
            print("Порт закрыт.")
        else:
            print("Порт уже закрыт или не был открыт.")


# Пример использования
if __name__ == "__main__":
    SerialSender.open_port(PortScanner.find_arduino_port())  # Открытие порта
    SerialSender.send_data("Привет, COM-порт!")  # Отправка данных
    SerialSender.send_data("Еще данные!")  # Отправка других данных
    SerialSender.close_port()  # Закрытие порта, когда он больше не нужен
