import cv2
from time import perf_counter
import numpy as np
from PIL import Image
from picamera2 import Picamera2

def hsv_to_range(hsv):
    # blue = [219*179//360, 0.93*255, 0.41*255]
    hsv = [hsv[0]*179//360, hsv[1]/100*255, hsv[2]/100*255]
    return np.array([hsv[0] - 20, hsv[1] - 100, hsv[2] - 100]), np.array([hsv[0] + 20, hsv[1] + 100, hsv[2] + 100])


picam = Picamera2()
picam.preview_configuration.main.size=(320, 180)
picam.preview_configuration.main.format="RGB888"
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

t = perf_counter()
orange = [28,100,100]
orange_low, orange_up = hsv_to_range(orange)
blue = [219, 93, 41]
blue_lower_hsv, blue_upper_hsv = hsv_to_range(blue)
yellow = [66, 100, 100]
yellow_low, yellow_up = hsv_to_range(yellow)

while perf_counter()-t:
    frame = picam.capture_array()

    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #mask = cv2.inRange(hsv_image, orange_low, orange_up)
    #mask = cv2.inRange(hsv_image, blue_lower_hsv, blue_upper_hsv)
    mask = cv2.inRange(frame, yellow_low, yellow_up)

    mask_ = Image.fromarray(mask)

    bbox = mask_.getbbox()

    if bbox:
        x1, y1, x2, y2 = bbox

        frame = cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0), 3)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()