import math
import cv2
import random
from ultralytics import YOLO
import capture
import threading
import time
import wait_for_fire
from wifi_manager import *
import numpy as np


class TurretControl:
    fps = 25
    num = 0
    angleX = 90
    angleY = 90
    xDirection = -1
    yDirection = 15
    in_diapason_x = True
    in_diapason_y = True
    xRotate = 1
    yRotate = 1
    is_shooting = False
    remote_control = False
    model = None
    maxX, minX = 90, 0
    maxY, minY = 120, 65

    @staticmethod
    def send_command(dx, dy, shoot):
        TurretControl.angleX += dx
        TurretControl.angleY += dy
        TurretControl.angleX = max(TurretControl.minX, min(TurretControl.maxX, TurretControl.angleX))
        TurretControl.angleY = max(TurretControl.minY, min(TurretControl.maxY, TurretControl.angleY))
        msg = f"!{TurretControl.angleX}@{TurretControl.angleY}#{shoot};"
        # SEND
        WiFiTaskManager.send_data(msg)

    @staticmethod
    def aim(x_start, y_start, x_end, y_end, center_x, center_y):
        if x_start <= center_x <= x_end and y_start <= center_y <= y_end:
            print("SHOOTING")
            TurretControl.is_shooting = True
            spray_width = 5
            shoot_thread = threading.Thread(target=TurretControl.shoot, args=(spray_width,))
            shoot_thread.start()
        else:
            dx, dy = 0, 0
            if center_x < x_start:
                dx = 1 * TurretControl.xRotate
            elif center_x > x_end:
                dx = -1 * TurretControl.xRotate
            if center_y < y_start:
                dy = 1 * TurretControl.yRotate
            elif center_y > y_end:
                dy = -1 * TurretControl.yRotate

            TurretControl.angleX += dx
            TurretControl.angleY += dy
            TurretControl.angleX = max(TurretControl.minX, min(TurretControl.maxX, TurretControl.angleX))
            TurretControl.angleY = max(TurretControl.minY, min(TurretControl.maxY, TurretControl.angleY))
            shoot_str = '#0;'
            dim = round((x_end - x_start) / 2)
            if x_start - dim <= center_x <= x_end + dim and y_start - dim <= center_y <= y_end + dim:
                shoot_str = '#1;'
            msg = f"!{TurretControl.angleX}@{TurretControl.angleY}" + shoot_str
            # SEND
            WiFiTaskManager.send_data(msg)
            print("AIMING", msg)

    @staticmethod
    def shoot(spray_width):
        spray_width += 1
        x_start = TurretControl.angleX - math.trunc(spray_width / 2)
        x_end = TurretControl.angleX + math.trunc(spray_width / 2)
        y_start = TurretControl.angleY
        y_end = TurretControl.angleY + math.trunc(spray_width) * 4
        y_before = TurretControl.angleY
        step_y = 1 if y_end - y_start > 0 else -1
        step_x = 1 if x_end - x_start > 0 else -1

        for y in range(y_start, y_end, step_y):
            for x in range(x_start, x_end, step_x):
                msg = f"!{x}@{y}#1;"
                print(msg)
                TurretControl.angleX = x
                TurretControl.angleY = y
                # SEND
                WiFiTaskManager.send_data(msg)
                time.sleep(0.02)
            buf = x_start
            x_start = x_end
            x_end = buf
            step_x *= -1

        TurretControl.angleY = y_before
        msg = f"!{TurretControl.angleX}@{TurretControl.angleY}#0;"
        # SEND
        WiFiTaskManager.send_data(msg)
        TurretControl.is_shooting = False
        print("DONEEEEEEEEEE")

    @staticmethod
    def search():
        if TurretControl.angleX >= TurretControl.maxX:
            TurretControl.angleX = TurretControl.maxX
            TurretControl.xDirection = abs(TurretControl.xDirection) * -1 * TurretControl.xRotate
            TurretControl.angleY += TurretControl.yDirection * TurretControl.yRotate
        if TurretControl.angleX <= TurretControl.minX:
            TurretControl.angleX = TurretControl.minX
            TurretControl.xDirection = abs(TurretControl.xDirection) * TurretControl.xRotate
            TurretControl.angleY += TurretControl.yDirection * TurretControl.yRotate
        if TurretControl.angleY >= TurretControl.maxY:
            TurretControl.angleY = TurretControl.maxY
            TurretControl.yDirection = abs(TurretControl.yDirection) * -1 * TurretControl.yRotate
        if TurretControl.angleY <= TurretControl.minY:
            TurretControl.angleY = TurretControl.minY
            TurretControl.yDirection = abs(TurretControl.yDirection) * TurretControl.yRotate
        TurretControl.angleX += TurretControl.xDirection * TurretControl.xRotate
        msg = f"!{TurretControl.angleX}@{TurretControl.angleY}#0;"
        # SEND
        WiFiTaskManager.send_data(msg)
        print("SEARCHING", msg)

    @staticmethod
    def recognize_fire(img_resp):
        # img_resp = WiFiTaskManager.get_img_from_cam()
        imgnp = np.array(bytearray(img_resp.content), dtype=np.uint8)
        # Decode the image to a format suitable for OpenCV
        frame = cv2.imdecode(imgnp, -1)
        if img_resp.status_code != 200:
            print("cant grab frame")
            return None
        results = TurretControl.model.track(frame, conf=0.5, iou=0.6, persist=True, verbose=False, tracker="botsort.yaml")
        sight_dimention = round(min(frame.shape[0], frame.shape[1]) * 0.1)
        kx, ky = 0 * sight_dimention, 0 * sight_dimention
        sight_coordinates = [round((frame.shape[1] - sight_dimention) / 2 + kx),
                             round((frame.shape[0] - sight_dimention) / 2 + 2.5 * ky),
                             round((frame.shape[1] - sight_dimention) / 2 + kx + sight_dimention),
                             round((frame.shape[0] - sight_dimention) / 2 + 2.5 * ky + sight_dimention)]

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            confs = results[0].boxes.conf
            center = (round((boxes[0][0] + boxes[0][2]) / 2), round((boxes[0][1] + boxes[0][3]) / 2))
            if not TurretControl.is_shooting:
                TurretControl.aim(*sight_coordinates, center[0], center[1])
            for box, id, conf in zip(boxes, ids, confs):
                # Generate a random color for each object based on its ID
                x_start, y_start, x_end, y_end = box[0], box[1], box[2], box[3],
                random.seed(int(id))
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                # cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3],), color, 2)
                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end,), color, 2)
                print(TurretControl.num, conf * 100, results[0].boxes.cls, id)
                TurretControl.num += 1
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
        elif not TurretControl.is_shooting and not wait_for_fire.wait(results[0].boxes.id is not None):
            TurretControl.search()
        capture.capture_fire(results[0].boxes.id != None, (int(frame.shape[1]), int(frame.shape[0])), TurretControl.fps, frame)
        frame = cv2.rectangle(frame, (sight_coordinates[0], sight_coordinates[1]),
                              (sight_coordinates[2], sight_coordinates[3]), (0, 255, 0), 5)
        frame = cv2.rectangle(frame,
                              (sight_coordinates[0] - sight_dimention, sight_coordinates[1] - sight_dimention),
                              (sight_coordinates[2] + sight_dimention, sight_coordinates[3] + sight_dimention),
                              (0, 255, 255), 5)
        # if show_video:
        #     frame = cv2.resize(frame, (0, 0), fx=1.5, fy=1.5)
        #     cv2.imshow("frame", frame)

        return frame
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break
        # cv2.destroyAllWindows()

    @staticmethod
    def initialize_model(*, model_path: str):
        TurretControl.model = YOLO(model_path)
        TurretControl.model.fuse()
        # TurretControl.send_fire_xy(model, cam_num, True)

    @staticmethod
    def release_video_capture():
        try:
            capture.out.release()
        except AttributeError:
            print('no video was recording')


# Запуск системы
# TurretControl.start(model_path="../models_fire_detection_datasetv5/best2.pt")
