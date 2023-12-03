import cv2
import numpy as np
from picamera2 import Picamera2

def hsv_to_range(hsv):
    hsv = [hsv[0] * 179 // 360, hsv[1] / 100 * 255, hsv[2] / 100 * 255]
    return np.array([hsv[0] - 10, hsv[1] - 65, hsv[2] - 65]), np.array(
        [hsv[0] + 10, hsv[1] + 65, hsv[2] + 65]
    )


def process_hole(img):
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    hole_hsv = [345, 85, 75]
    low_hole, high_hole = hsv_to_range(hole_hsv)

    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv_img, low_hole, high_hole)

    # Blur the mask
    mask = cv2.GaussianBlur(mask, (11, 11), 0)

    # Apply a threshold to the frame
    _, threshold = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return img, _
    
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Approximate a polygon for the contour
    poly = cv2.approxPolyDP(contours[0], 0.01 * cv2.arcLength(contours[0], True), True)
    
    if len(poly) < 6:
        return img, _
    
    # # Draw contours joining the points
    # img = cv2.drawContours(img, [contours], -1, (0, 255, 0), 2)

    # Find bbox
    x, y, w, h = cv2.boundingRect(contours[0])
    bbox = [x, y, x + w, y + h]

    # Draw bbox
    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return img, bbox


def main():
    # Open video capture
    picam = Picamera2()
    picam.preview_configuration.main.size=(1280, 720)
    picam.preview_configuration.main.format="RGB888"
    picam.preview_configuration.align()
    picam.configure("preview")
    picam.start()


    while True:
        # Read the next frame
        frame = picam.capture_array()

        # Process the frame
        frame, _ = process_hole(frame)

        # Show the frame
        cv2.imshow("Frame", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
