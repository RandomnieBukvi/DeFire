import math

import cv2                              # библиотека opencv (получение и обработка изображения)
import serial                           # библиотека pyserial (отправка и прием информации)
import random
from ultralytics import YOLO
import capture
import threading
import time
import wait_for_fire
# 5 - справа дальше / 4 - слева / 3 - справа ближе
portNo = "COM4"
uart = serial.Serial(portNo, 9600)      # инициализируем последовательный порт на скорости 9600 Бод

angleX = 90
angleY = 50

xDirection = -1  # на сколько поворачивать каждую ось при поиске
yDirection = 15

in_diapason_x = True
in_diapason_y = True

xRotate = 1 #нужно ли отзеркаливать движение32
yRotate = -1

is_shooting = False


def aim(x_start, y_start, x_end, y_end, center_x, center_y):
    global angleX, angleY, is_shooting  # Объявляем angleX и angleY как глобальные
    print(x_start, y_start, x_end, y_end, center_x, center_y)
    #x_start <= center_x <= x_end and y_start <= center_y <= y_end
    if x_start <= center_x <= x_end and y_start <= center_y <= y_end:
        # msg = bytes(str(f"!{angleX}@{angleY}#1;"), 'utf-8')
        # uart.write(msg)
        # print("SHOOTING", msg)
        print("SHOOTING")
        is_shooting = True
        closer_left = abs(center_x - x_start) < abs(center_x - x_end)
        closer_top = abs(center_y - y_start) < abs(center_y - y_end)
        spray_width = 5
        shoot_thread = threading.Thread(target=shoot, args=(closer_left, closer_top, spray_width))
        shoot_thread.start()
    else:
        dx = 0
        dy = 0
        if center_x < x_start:
            dx = 1 * xRotate
        elif center_x > x_end:
            dx = -1 * xRotate
        if center_y < y_start:
            dy = 1 * yRotate
        elif center_y > y_end:
            dy = -1 * yRotate

        angleX += dx
        angleY += dy

        if angleX > 150:
            angleX = 150
        if angleX < 0:
            angleX = 0
        if angleY > 70:
            angleY = 70
        if angleY < 5:
            angleY = 5
        shoot_str = '#0;'
        dim = round((x_end - x_start) / 2)
        if x_start - dim <= center_x <= x_end + dim and y_start - dim <= center_y <= y_end + dim:
            shoot_str = '#1;'
        msg = f"!{angleX}@{angleY}" + shoot_str
        msg = bytes(str(msg), 'utf-8')
        uart.write(msg)
        print("AIMING", msg)


def shoot(closer_left: bool, closer_top: bool, spray_width: int):
    global xRotate, yRotate, angleX, angleY, is_shooting
    x_start = 0
    y_start = 0
    spray_width += 1
    # if closer_left:
    #     x_start = angleX
    #     x_end = angleX + (spray_width * xRotate)
    # else:
    #     x_start = angleX
    #     x_end = angleX - (spray_width * xRotate)
    # if not closer_top:
    #     y_start = angleY
    #     y_end = angleY + (spray_width * 2 * yRotate)
    # else:
    #     y_start = angleY + (spray_width * 2 * yRotate)
    #     y_end = angleY
    x_start = angleX - math.trunc(spray_width / 2)
    x_end = angleX + math.trunc(spray_width / 2)
    y_start = angleY # + math.trunc(spray_width) #!!!!!!!!!!!!!!!!!!! не забудь проверить атаку турели(добавил * yRotate)
    y_end = angleY - math.trunc(spray_width) * 4
    y_before = angleY
    step_y = 0
    step_x = 0
    if y_end - y_start > 0:
        step_y = 1
    else:
        step_y = -1
    if x_end - x_start > 0:
        step_x = 1
    else:
        step_x = -1
    angle_x_start = angleX
    angle_y_start = angleY
    for y in range(y_start, y_end, step_y):
        for x in range(x_start, x_end, step_x):
            msg = f"!{x}@{y}#1;"
            msg = bytes(str(msg), 'utf-8')
            angleX = x
            angleY = y
            uart.write(msg)
            print(msg)
            time.sleep(0.02)
        buf = x_start
        x_start = x_end
        x_end = buf
        step_x *= -1
    # angleX = x_end - (1 * xRotate * -1)
    # angleY = y_end - (1 * yRotate * -1)
    angleY = y_before
    msg = f"!{angleX}@{angleY}#0;"
    msg = bytes(str(msg), 'utf-8')
    is_shooting = False
    print("DONEEEEEEEEEE")


def search():
    global angleX, angleY, in_diapason_x, in_diapason_y  # Объявляем angleX и angleY как глобальные
    global xDirection, yDirection, xRotate, yRotate
    # if angleX >= 180 or angleX <= 0:
    #     if in_diapason_x:
    #         xDirection *= -1
    #         angleY += yDirection * yRotate
    #         in_diapason_x = False
    # else:
    #     in_diapason_x = True
    # if angleY >= 110 or angleY <= 60:
    #     if in_diapason_y:
    #         yDirection *= -1
    #         in_diapason_y = False
    # else:
    #     in_diapason_y = True
    if angleX >= 150:
        angleX = 150
        xDirection = abs(xDirection) * -1 * xRotate
        #angleY += yDirection * yRotate
    if angleX <= 0:
        angleX = 0
        xDirection = abs(xDirection) * xRotate
        #angleY += yDirection * yRotate
    if angleY >= 70:
        angleY = 70
        yDirection = abs(yDirection) * -1 * yRotate
    if angleY <= 5:
        angleY = 5
        yDirection = abs(yDirection) * yRotate
    print(angleX, angleY, xDirection, yDirection)
    print(f'in_diapason_x: {in_diapason_x}, in_diapason_y: {in_diapason_y}')
    angleX += xDirection * xRotate
    msg = f"!{angleX}@{angleY}#0;"
    msg = bytes(str(msg), 'utf-8')
    uart.write(msg)
    print("SEARCHING", msg)


def send_fire_xy(model, cam_num, show_video=True):
    # Open the input video file
    cap = cv2.VideoCapture(cam_num)
    if not cap.isOpened():
        raise Exception("Error: Could not open cam.")
    cap.read()
    cap.read()
    cap.read()
    cap.read()
    cap.read()

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    num = 0
    while True:
        ret, frame = cap.read()

        if not ret:
            print("cant grab frame")
            continue
        results = model.track(frame, conf=0.5, iou=0.6, persist=True, verbose=False, tracker="botsort.yaml")
        sight_dimention = round(min(frame.shape[0], frame.shape[1]) * 0.1)
        # k = sight_dimention * 1.5
        kx = 0 * sight_dimention
        ky = 0 * sight_dimention
        sight_coordinates = [round((frame.shape[1] - sight_dimention) / 2 + kx),
                             round((frame.shape[0] - sight_dimention) / 2 + 2.5 * ky),
                             round((frame.shape[1] - sight_dimention) / 2 + kx + sight_dimention),
                             round((frame.shape[0] - sight_dimention) / 2 + 2.5 * ky + sight_dimention)]
        if results[0].boxes.id != None:  # this will ensure that id is not None -> exist tracks
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            confs = results[0].boxes.conf
            center = (round((boxes[0][0] + boxes[0][2]) / 2), round((boxes[0][1] + boxes[0][3]) / 2))
            if not is_shooting:
                aim(*sight_coordinates, center[0], center[1])
            for box, id, conf in zip(boxes, ids, confs):
                # Generate a random color for each object based on its ID
                x_start, y_start, x_end, y_end = box[0], box[1], box[2], box[3],
                random.seed(int(id))
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                # cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3],), color, 2)
                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end,), color, 2)
                print(num, conf * 100, results[0].boxes.cls, id)
                num += 1
                cv2.putText(
                    frame,
                    f"Id {id}, Confidence {conf * 100}",
                    (box[0], box[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    2,
                )
                center = (round((x_start + x_end) / 2), round((y_start + y_end) / 2))
                print(center)
                cv2.circle(frame, center, 5, (0, 0, 0), -1)
        elif not is_shooting and not wait_for_fire.wait(results[0].boxes.id != None):
            search()
            print("EFHFUHEEFEFFE------------------------------")
        capture.capture_fire(results[0].boxes.id != None, (int(cap.get(3)), int(cap.get(4))), fps, frame)
        frame = cv2.rectangle(frame, (sight_coordinates[0], sight_coordinates[1]),
                              (sight_coordinates[2], sight_coordinates[3]), (0, 255, 0), 5)
        frame = cv2.rectangle(frame, (sight_coordinates[0] - sight_dimention, sight_coordinates[1] - sight_dimention),
                              (sight_coordinates[2] + sight_dimention, sight_coordinates[3] + sight_dimention), (0, 255, 255), 5)
        if show_video:
            frame = cv2.resize(frame, (0, 0), fx=1.5, fy=1.5)
            cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the input video capture and output video writer
    try:
        capture.out.release()
    except AttributeError:
        print('no video was recording')
    cap.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()


def start(*, model_path: str, cam_num: int = 0):
    # Example usage:
    model = YOLO(model_path)
    model.fuse()
    send_fire_xy(model, cam_num, True)


start(model_path="../models_fire_detection_datasetv5/best2.pt", cam_num=1)
