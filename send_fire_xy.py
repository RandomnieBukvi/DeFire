import cv2                              # библиотека opencv (получение и обработка изображения)
import serial                           # библиотека pyserial (отправка и прием информации)
import random
from ultralytics import YOLO

portNo = "COM4"
uart = serial.Serial(portNo, 9600)      # инициализируем последовательный порт на скорости 9600 Бод


def send_fire_xy(model, cam_num, show_video=True):
    # Open the input video file
    cap = cv2.VideoCapture(cam_num)

    if not cap.isOpened():
        raise Exception("Error: Could not open cam.")

    # Get input video frame rate and dimensions
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model.track(frame, conf=0.5, iou=0.6, persist=True, verbose=False, tracker="botsort.yaml")

        if results[0].boxes.id != None:  # this will ensure that id is not None -> exist tracks
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            confs = results[0].boxes.conf
            for box, id, conf in zip(boxes, ids, confs):
                # Generate a random color for each object based on its ID
                x_start, y_start, x_end, y_end = box[0], box[1], box[2], box[3],
                random.seed(int(id))
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                # cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3],), color, 2)
                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end,), color, 2)
                print(num ,conf * 100, results[0].boxes.cls, id)
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

                msg = f'!{center[0]}@{center[1]};'
                #             # ! - означает что сейчас будут координаты центра лица по x
                #             # @ - означает что сейчас будут координаты центра лица по y
                #             # ; - означает что это конец сообщения
                #
                msg = bytes(str(msg), 'utf-8')
                uart.write(msg)
                print(msg)

        if show_video:
            frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
            cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the input video capture and output video writer
    cap.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()


def start(*, model_path: str, cam_num: int = 0):
    # Example usage:
    model = YOLO(model_path)
    model.fuse()
    send_fire_xy(model, cam_num, True)


start(model_path="../models_fire_detection_datasetV4/best.pt", cam_num=0)


# with mp_face_detection.FaceDetection(
#         model_selection=0, min_detection_confidence=0.5) as face_detection:
#     while True:
#         ret, frame = camera.read()
#         temp_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = face_detection.process(temp_frame)
#         x_start, y_start, x_end, y_end = 0, 0, 0, 0
#         if results.detections:
#             for detection in results.detections:
#                 box = detection.location_data.relative_bounding_box
#                 x_start, y_start = int(box.xmin * frame.shape[1]), int(box.ymin * frame.shape[0])
#                 x_end, y_end = int((box.xmin + box.width) * frame.shape[1]), int(
#                     (box.ymin + box.height) * frame.shape[0])
#                 frame = cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 5)
#                 score = str(detection.score)[3:5] + "%"
#                 txt_coords = (x_start - 20, y_start - 20)
#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 scale = 1
#                 txt_col = (255, 0, 0)
#                 thickness = 2
#                 cv2.putText(frame, score, txt_coords, font, scale, txt_col, thickness, cv2.LINE_AA)
#                 center = (round((x_start + x_end) / 2), round((y_start + y_end) / 2))
#                 cv2.circle(frame, center, 5, (0, 0, 255), -1)
#
#             msg = f'!{center[0]}@{center[1]};'
#             # ! - означает что сейчас будут координаты центра лица по x
#             # @ - означает что сейчас будут координаты центра лица по y
#             # ; - означает что это конец сообщения
#
#             msg = bytes(str(msg), 'utf-8')
#             uart.write(msg)
#             print(msg)
#         cv2.imshow('test', frame)
#         if cv2.waitKey(1) == ord('q'):
#             break
