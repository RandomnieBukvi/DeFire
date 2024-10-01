import cv2
import tkinter as tk
from tkinter import Button
from PIL import Image, ImageTk
from turret_manager import *
from wifi_manager import *

# Инициализация OpenCV для получения изображения с камеры
# cap = cv2.VideoCapture(0)

# Глобальная переменная для переключения режимов
# manual_control = False


# Функция для обработки клавиш управления турелью
# def control_turret(event):
#     if TurretControl.remote_control:
#         dx, dy, shoot = 0, 0, 0
#         if event.keysym == 'w':
#             dy = 1
#             print("Move turret forward")
#         elif event.keysym == 's':
#             dy = -1
#             print("Move turret backward")
#         if event.keysym == 'a':
#             dx = -1
#             print("Move turret left")
#         elif event.keysym == 'd':
#             dx = 1
#             print("Move turret right")
#         if event.keysym == 'space':
#             shoot = 1
#             print("Fire!")
#         TurretControl.send_command(dx, dy, shoot)
#     else:
#         print("Manual control is off. No actions will be taken.")


# Функция для переключения управления
# def toggle_control():
#     TurretControl.remote_control = not TurretControl.remote_control
#     TurretControl.is_shooting = False
#     control_status.set(f"Manual control: {'ON' if TurretControl.remote_control else 'OFF'}")
#     print(f"Manual control {'enabled' if TurretControl.remote_control else 'disabled'}")


# current_image = None


# Функция для отображения изображения с камеры
# def update_frame():
#     global current_image
#     img_resp = WiFiTaskManager.get_img_from_cam()
#     if img_resp.status_code != 200:
#         print('NGERS')
#     # Convert the response content to a NumPy array
#     imgnp = np.array(bytearray(img_resp.content), dtype=np.uint8)
#     # Decode the image to a format suitable for OpenCV
#     im = cv2.imdecode(imgnp, -1)
#     im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
#     img = Image.fromarray(im)
#     current_image = img
#     imgtk = ImageTk.PhotoImage(image=img)
#     lbl_video.imgtk = imgtk  # Сохраняем ссылку
#     lbl_video.config(image=imgtk)  # Отображаем изображение
#     root.after(10, update_frame)  # Обновляем кадр каждые 10 мс


# def autoresize_image(event):
#     # lbl_video.config(width=event.width, height=event.height)
#     if current_image is None:
#         return
#     print('RESIZE')
#     resized_image = current_image.resize((lbl_video.winfo_width(), lbl_video.winfo_height()))
#
#     # Преобразуем изображение в формат Tkinter
#     imgtk = ImageTk.PhotoImage(image=resized_image)
#
#     # Обновляем изображение в метке
#     lbl_video.imgtk = imgtk
#     lbl_video.config(image=imgtk)

class GUI:
    root = None
    control_status = None
    lbl_status = None
    btn_toggle = None
    lbl_video = None
    original_image = None
    @staticmethod
    def initialize():
        GUI.root = tk.Tk()
        GUI.root.title("Turret Control Interface")
        GUI.control_status = tk.StringVar(value="Manual control: OFF")
        GUI.lbl_status = tk.Label(GUI.root, textvariable=GUI.control_status)
        GUI.lbl_status.pack()
        GUI.btn_toggle = Button(GUI.root, text="Toggle Control", command=GUI.toggle_control)
        GUI.btn_toggle.pack()
        GUI.lbl_video = tk.Label(GUI.root)
        GUI.lbl_video.pack(fill=tk.BOTH, expand=True)
        GUI.root.bind('<KeyPress>', GUI.control_turret)
        # GUI.root.bind('<Configure>', GUI.resize_image)
        GUI.update_frame()
        GUI.root.mainloop()

    @staticmethod
    def control_turret(event):
        if TurretControl.remote_control:
            dx, dy, shoot = 0, 0, 0
            if event.keysym == 'w':
                dy = 1
                print("Move turret forward")
            elif event.keysym == 's':
                dy = -1
                print("Move turret backward")
            if event.keysym == 'a':
                dx = 1
                print("Move turret left")
            elif event.keysym == 'd':
                dx = -1
                print("Move turret right")
            if event.keysym == 'space':
                shoot = 1
                print("Fire!")
            elif event.keysym != 'space':
                shoot = 0
                print("Fire!")
            TurretControl.send_command(dx, dy, shoot)
        else:
            print("Manual control is off. No actions will be taken.")

    @staticmethod
    def toggle_control():
        TurretControl.remote_control = not TurretControl.remote_control
        TurretControl.is_shooting = False
        GUI.control_status.set(f"Manual control: {'ON' if TurretControl.remote_control else 'OFF'}")
        print(f"Manual control {'enabled' if TurretControl.remote_control else 'disabled'}")

    @staticmethod
    def update_frame():
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

        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(im)
        GUI.original_image = img#.copy()
        imgtk = ImageTk.PhotoImage(image=img)
        GUI.lbl_video.imgtk = imgtk  # Сохраняем ссылку
        GUI.lbl_video.config(image=imgtk)  # Отображаем изображение
        GUI.root.after(10, GUI.update_frame)  # Обновляем кадр каждые 10 мс

    @staticmethod
    def resize_image(event):
        # Get the new window size
        new_width = event.width
        new_height = event.height

        # Resize the image to fit the window
        resized_image = GUI.original_image.resize((new_width, new_height)) # Image.ANTIALIAS

        imgtk = ImageTk.PhotoImage(image=resized_image)
        GUI.lbl_video.imgtk = imgtk  # Сохраняем ссылку
        GUI.lbl_video.config(image=imgtk)  # Отображаем изображение

    # WiFiTaskManager.receive_broadcast()

# Инициализация Tkinter
# root = tk.Tk()
# root.title("Turret Control Interface")
#
# # Метка для отображения статуса управления
# control_status = tk.StringVar(value="Manual control: OFF")
# lbl_status = tk.Label(root, textvariable=control_status)
# lbl_status.pack()
#
# # Кнопка для переключения режима управления
# btn_toggle = Button(root, text="Toggle Control", command=toggle_control)
# btn_toggle.pack()
#
# # Метка для отображения изображения с камеры
# lbl_video = tk.Label(root)
# lbl_video.pack(fill=tk.BOTH, expand=True)
#
# # Привязка событий
# root.bind('<KeyPress>', control_turret)
# # root.bind('<Configure>', autoresize_image)
#
# # Запуск обновления изображения
# update_frame()
#
# # Запуск основного цикла Tkinter
# root.mainloop()
