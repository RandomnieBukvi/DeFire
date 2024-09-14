import time

import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from wifi_manager import *


def update_frame():
    img_resp = WiFiTaskManager.get_img_from_cam()
    # Convert the response content to a NumPy array
    imgnp = np.array(bytearray(img_resp.content), dtype=np.uint8)
    # Decode the image to a format suitable for OpenCV
    im = cv2.imdecode(imgnp, -1)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(im)
    imgtk = ImageTk.PhotoImage(image=img)
    lbl_video.imgtk = imgtk  # Сохраняем ссылку
    lbl_video.config(image=imgtk)  # Отображаем изображение
    root.after(10, update_frame)  # Обновляем кадр каждые 10 мс


def key_event(event):
    if event.char == 'q':
        root.quit()
    elif event.char == 'a':
        WiFiTaskManager.send_data('on')
    elif event.char == 's':
        WiFiTaskManager.send_data('off')

WiFiTaskManager.receive_broadcast()

# Инициализация Tkinter
root = tk.Tk()
root.bind('<Key>', key_event)  # Привязываем событие клавиши
lbl_video = tk.Label(root)
lbl_video.pack()

# Обновляем изображение
update_frame()

# Запуск цикла Tkinter
root.mainloop()