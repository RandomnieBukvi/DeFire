import cv2
import time
import datetime
import convert
import threading

detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 10
fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = None
current_time = None


def capture_fire(fire_exists: bool, frame_size: tuple, fps: int, frame):
    global detection, detection_stopped_time, timer_started, SECONDS_TO_RECORD_AFTER_DETECTION, fourcc, out, current_time
    if fire_exists:
        if detection:
            timer_started = False
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d.%m.%Y %H-%M-%S")
            send_photo_thread = threading.Thread(target=convert.save_photo_and_send, args=(frame, f"../photos/{current_time}.jpg", current_time))
            send_photo_thread.start()
            out = cv2.VideoWriter(
                f"../videos/avi/{current_time}.avi", fourcc, fps, frame_size)
            print("Started Recording!")
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                print('Stop Recording!')
                send_video_thread = threading.Thread(target=convert.avi_to_mp4_and_send, args=(
                    f"../videos/avi/{current_time}.avi", fps, f"../videos/mp4/{current_time}.mp4", current_time))
                send_video_thread.start()
                # convert.avi_to_mp4_and_send(f"videos/avi/{current_time}.avi",
                #                             fps, f"videos/mp4/{current_time}.mp4", current_time)
        else:
            timer_started = True
            detection_stopped_time = time.time()

    if detection:
        out.write(frame)

