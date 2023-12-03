import cv2
import numpy as np
from picamera2 import Picamera2


def check_ball_in_hole(ball_box, hole_box):
    '''
    Checks if ball is inside hole
    :param ball_box: bounding box of ball
    :param hole_box: bounding box of hole

    It will see the area in common between the two boxes.
    This area will be delimited by the two x center coordinates and the two y center coordinates.
    For example: ball_box = [x1_1, y1_1, x1_2, y1_2], hole_box = [x2_1, y2_1, x2_2, y2_2]
    Let's say x1_1 < x2_1 < x1_2 < x2_2, then the x coordinates of the common area will be [x2_1, x1_2]
    The same applies for the y coordinates.

    Then, if this area is greater than 80% of the area of the ball, the ball is inside the hole
    '''

    # Get the coordinates of the common area
    x1_1, y1_1, x1_2, y1_2 = ball_box
    x2_1, y2_1, x2_2, y2_2 = hole_box

    if x1_2 < x2_1 or x1_1 > x2_2 or y1_2 < y2_1 or y1_1 > y2_2:
        return False

    # Sort x coordinates
    x_coords = sorted([x1_1, x1_2, x2_1, x2_2])
    x1, x2 = x_coords[1], x_coords[2]

    # Sort y coordinates
    y_coords = sorted([y1_1, y1_2, y2_1, y2_2])
    y1, y2 = y_coords[1], y_coords[2]

    # Calculate the area of the common area
    common_area = (x2 - x1) * (y2 - y1)

    # Calculate the area of the ball
    ball_area = (x1_2 - x1_1) * (y1_2 - y1_1)

    # If the common area is greater than 80% of the area of the ball, the ball is inside the hole
    return common_area >= 0.8 * ball_area


def hsv_to_range(hsv):
    hsv = [hsv[0]*179//360, hsv[1]/100*255, hsv[2]/100*255]
    return np.array([hsv[0] - 30, hsv[1] - 150, hsv[2] - 150]), np.array([hsv[0] + 30, hsv[1] + 150, hsv[2] + 150])


def process_hole(img, hsv_img):
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Hole filter
    hole_hsv = [345, 85, 75]
    low_hole, high_hole = hsv_to_range(hole_hsv)

    # Create a mask for the hole color
    mask = cv2.inRange(hsv_img, low_hole, high_hole)

    # Blur the mask
    mask = cv2.GaussianBlur(mask, (11, 11), 0)

    # Apply a threshold to the frame
    _, threshold = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)

    # Find contours of the thresholded frame
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return img, _
    
    # Sort contours by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Approximate a polygon for the contour
    poly = cv2.approxPolyDP(contours[0], 0.01 * cv2.arcLength(contours[0], True), True)
    if len(poly) < 6:
        return img, _
    
    # Draw contours joining the points
    # img = cv2.drawContours(img, [contours], -1, (0, 255, 0), 2)

    # Find bbox
    x, y, w, h = cv2.boundingRect(contours[0])
    bbox = (x, y, x + w, y + h)

    # Draw bbox
    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return img, bbox


def process_ball(img, hsv_img):
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Yellow filter
    yellow = [66, 100, 100]
    yellow_low, yellow_up = hsv_to_range(yellow)

    # Create a mask for the yellow color
    mask = cv2.inRange(hsv_img, yellow_low, yellow_up)

    # Blur the mask
    mask = cv2.GaussianBlur(mask, (11, 11), 0)

    # Apply a threshold to the frame
    _, threshold = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)

    # Find contours of the thresholded frame
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return img, _
    
    # Sort contours by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Approximate a polygon for the contour
    poly = cv2.approxPolyDP(contours[0], 0.01 * cv2.arcLength(contours[0], True), True)
    if len(poly) < 6:
        return img, _
    
    # Draw contours joining the points
    # img = cv2.drawContours(img, [contours], -1, (0, 255, 0), 2)

    # Find bbox
    x, y, w, h = cv2.boundingRect(contours[0])
    bbox = (x, y, x + w, y + h)

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

    print('Searching for ball and hole...')
    while True:
        # Read the next frame
        frame = picam.capture_array()

        # Convert frame to hsv
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Process the frame
        frame, hole_bbox = process_hole(frame, hsv_image)
        frame, ball_bbox = process_ball(frame, hsv_image)

        # Check if ball detected
        ball_detected = False
        if type(ball_bbox) is tuple:
            ball_detected = len(ball_bbox) == 4

        # Check if hole detected
        hole_detected = False
        if type(hole_bbox) is tuple:
            hole_detected = len(hole_bbox) == 4

        # Check if ball is inside hole
        if ball_detected and hole_detected:
            if check_ball_in_hole(ball_bbox, hole_bbox):
                print('\033[1A\033[2K', end='')
                print("Ball is inside hole")
            else:
                print('\033[1A\033[2K', end='')
                print("Ball is not inside hole")
        else:
            print('\033[1A\033[2K', end='')
            print("Searching for ball and hole...")

        # Show the frame with bounding rectangles
        cv2.imshow('Frame', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()