import cv2
import time
import datetime
import threading

detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 2
current_time = None


def wait(fire_exists: bool) -> bool:
    do_wait = False
    global detection, detection_stopped_time, timer_started, SECONDS_TO_RECORD_AFTER_DETECTION
    if fire_exists:
        if detection:
            timer_started = False
        else:
            detection = True
            print("start waiting for fire")
        do_wait = False
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False

                print('Stop Recording!')
                do_wait = False
            else:
                do_wait = True
        else:
            timer_started = True
            detection_stopped_time = time.time()
            do_wait = True

    return do_wait

