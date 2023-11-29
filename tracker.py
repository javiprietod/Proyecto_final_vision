import cv2
import numpy as np
from PIL import Image
from picamera2 import Picamera2


# Function to check if a specific pattern is present in the frame
def check_pattern(frame, pattern):
    # Convert the pattern to grayscale
    pattern_gray = cv2.cvtColor(pattern, cv2.COLOR_BGR2GRAY)

    # Create SIFT object
    sift = cv2.SIFT_create()

    # Detect keypoints and compute descriptors for the pattern
    keypoints_pattern, descriptors_pattern = sift.detectAndCompute(pattern_gray, None)

    # Convert the frame to grayscale
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect keypoints and compute descriptors for the frame
    keypoints_frame, descriptors_frame = sift.detectAndCompute(frame_gray, None)

    # Create a BFMatcher object
    bf = cv2.BFMatcher()

    # Match descriptors of the pattern and frame
    matches = bf.match(descriptors_pattern, descriptors_frame)

    # Sort the matches by distance
    matches = sorted(matches, key=lambda x: x.distance)

    # Draw the top matches on the frame
    matched_frame = cv2.drawMatches(pattern_gray, keypoints_pattern, frame_gray, keypoints_frame, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    # Show the matched frame
    cv2.imshow('Pattern Matching', matched_frame)

    # If pattern is found, print 'hello'
    if len(matches) > 0:
        print('hello')


def hsv_to_range(hsv):
    # blue = [219*179//360, 0.93*255, 0.41*255]
    hsv = [hsv[0]*179//360, hsv[1]/100*255, hsv[2]/100*255]
    return np.array([hsv[0] - 30, hsv[1] - 150, hsv[2] - 150]), np.array([hsv[0] + 30, hsv[1] + 150, hsv[2] + 150])


# Pattern to be matched
pattern = cv2.imread('path_to_pattern_image')

# Yellow filter
yellow = [66, 100, 100]
yellow_low, yellow_up = hsv_to_range(yellow)

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

    # Convert frame to hsv
    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the yellow color
    mask = cv2.inRange(frame, yellow_low, yellow_up)

    # Blur the mask
    mask = cv2.GaussianBlur(mask, (11, 11), 0)

    # Apply a threshold to the frame
    _, threshold = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)

    # Find contours of the thresholded frame
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for contour in contours:
        # Area of contour
        area = cv2.contourArea(contour)
        if area < 1000:
            continue
        
        # Approximate the contour
        approx_poly = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        if len(approx_poly) < 10:
            continue

        # Draw bounding rectangle around the contour
        x, y, w, h = cv2.boundingRect(approx_poly)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Show the frame with bounding rectangles
    cv2.imshow('Motion Detection', frame)

    # Perform pattern matching
    # check_pattern(frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
