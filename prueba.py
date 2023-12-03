import cv2
from picamera2 import Picamera2
import numpy as np


def isolate_color(friend):
    # blue = [220, 80, 40]
    yellow = [20, 100, 100]
    # green = [135, 70, 40]
    # red = [355, 85, 60]
    # purple = [280, 45, 45]

    # blue_mask = get_color_mask(friend, blue)
    yellow_mask = get_color_mask(friend, yellow)
    # green_mask = get_color_mask(friend, green)
    # red_mask = get_color_mask(friend, red)
    # purple_mask = get_color_mask(friend, purple)

    # blue_result = cv2.bitwise_and(friend, friend, mask=blue_mask)
    yellow_result = cv2.bitwise_and(friend, friend, mask=yellow_mask)
    # green_result = cv2.bitwise_and(friend, friend, mask=green_mask)
    # red_result = cv2.bitwise_and(friend, friend, mask=red_mask)
    # purple_result = cv2.bitwise_and(friend, friend, mask=purple_mask)

    # result = cv2.bitwise_or(blue_result, yellow_result)
    # result = cv2.bitwise_or(result, green_result)
    # result = cv2.bitwise_or(result, red_result)
    # result = cv2.bitwise_or(result, purple_result)
    result = yellow_result
    return result


def get_color_mask(friend, color):
    '''
    Returns the color mask of the image
    '''
    lower_hsv, upper_hsv = hsv_to_range(color)
    hsv_image = cv2.cvtColor(friend, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
    blur = cv2.GaussianBlur(mask, (11, 11), 0)
    _, threshold = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)
    return threshold


def hsv_to_range(hsv):
    hsv = [hsv[0]*179//360, hsv[1]/100*255, hsv[2]/100*255]
    return np.array([hsv[0] - 10, hsv[1] - 100, hsv[2] - 100]), np.array([hsv[0] + 10, hsv[1] + 100, hsv[2] + 100])


def main():
    picam = Picamera2()
    picam.preview_configuration.main.size=(1280, 720)
    picam.preview_configuration.main.format="RGB888"
    picam.preview_configuration.align()
    picam.configure("preview")
    picam.start()
    while True:
        frame = picam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_iso = isolate_color(frame)
        frame_iso = cv2.cvtColor(frame_iso, cv2.COLOR_RGB2BGR)
        cv2.imshow('Frame', frame)
        cv2.imshow('Frame iso', frame_iso)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()