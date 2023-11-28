import cv2
import numpy as np

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


# Pattern to be matched
pattern = cv2.imread('path_to_pattern_image')

# Open video capture
cap = cv2.VideoCapture('path_to_video_file')

# Read the first frame
ret, prev_frame = cap.read()

# Convert the frame to grayscale
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

# Initialize the motion detection flag
motion_detected = False

while True:
    # Read the next frame
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate the absolute difference between the current and previous frame
    frame_diff = cv2.absdiff(gray, prev_gray)

    # Apply a threshold to the frame difference
    _, threshold = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

    # Find contours of the thresholded frame
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate over the contours
    for contour in contours:
        # Filter contours based on area or other criteria if needed
        

        # Draw bounding rectangle around the contour
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Check if there is movement in the video
        motion_detected = True

    # Show the frame with bounding rectangles
    cv2.imshow('Motion Detection', frame)

    # Check if there is movement and perform pattern matching
    if motion_detected:
        check_pattern(frame)

    # Update the previous frame
    prev_gray = gray.copy()

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and destroy all windows
cap.release()
cv2.destroyAllWindows()
