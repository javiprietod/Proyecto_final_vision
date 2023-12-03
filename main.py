import calibration as cal
import pattern_detection as pd
import tracker as tr
import cv2
from picamera2 import Picamera2
import random


def calibrate_camera():
    '''
    Calibrate the camera
    '''
    # Calibrate the camera
    cal.calibrate()
    return


def check_pattern():
    return

def track(picam):
    print('Searching for ball and hole...')
    while True:
        # Read the next frame
        frame = picam.capture_array()

        # Convert frame to hsv
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Process the frame
        frame, hole_bbox = tr.process_hole(frame, hsv_image)
        frame, ball_bbox = tr.process_ball(frame, hsv_image)

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
            if tr.check_ball_in_hole(ball_bbox, hole_bbox):
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


def main():
    # Calibrate the camera
    calibrate_camera()

    # Open video capture
    picam = Picamera2()
    picam.preview_configuration.main.size=(1280, 720)
    picam.preview_configuration.main.format="RGB888"
    picam.preview_configuration.align()
    picam.configure("preview")
    picam.start()

    # Check if pattern is valid
    PATTERN = [random.randint(0, 2) for _ in range(4)]
    curr_idx = 0
    print('This is the pattern you need to follow: ')
    pd.password(PATTERN)
    while curr_idx < 4:
        frame = picam.capture_array()

        frame, pattern_check = pd.detect_pattern(frame, PATTERN[curr_idx])
        
        cv2.imshow('Frame', frame)
        
        if pattern_check:
            curr_idx += 1
        else:
            curr_idx = 0
            print('Wrong pattern, try again')
            print('This is the pattern you need to follow: ')
            pd.password(PATTERN)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

    # Track the ball
    track(picam)

    # Close video capture
    picam.stop()


if __name__ == "__main__":
    main()