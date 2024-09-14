import requests
import numpy as np
import cv2

def get_image_from_wifi_cam(url):
    img_resp = requests.get(url)
    # Convert the response content to a NumPy array
    imgnp = np.array(bytearray(img_resp.content), dtype=np.uint8)
    # Decode the image to a format suitable for OpenCV
    img = cv2.imdecode(imgnp, -1)
    return img, img_resp.status_code
