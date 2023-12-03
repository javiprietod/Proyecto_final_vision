import cv2
import numpy as np
import imageio
import glob
import matplotlib.pyplot as plt


def load_images(filenames):
    return [imageio.imread(filename) for filename in filenames]


def hsv_to_range(hsv):
    hsv = [hsv[0]*179//360, hsv[1]/100*255, hsv[2]/100*255]
    return np.array([hsv[0] - 10, hsv[1] - 50, hsv[2] - 50]), np.array([hsv[0] + 10, hsv[1] + 50, hsv[2] + 50])


def isolate_color(friend):
    blue = [219, 93, 41]
    yellow = [46, 100, 68]
    green = [137, 99, 31]
    red = [357, 96, 54]
    black = [192, 36, 5]
    purple = [267, 55, 46]

    blue_lower_hsv, blue_upper_hsv = hsv_to_range(blue)
    yellow_lower_hsv, yellow_upper_hsv = hsv_to_range(yellow)
    green_lower_hsv, green_upper_hsv = hsv_to_range(green)
    red_lower_hsv, red_upper_hsv = hsv_to_range(red)
    black_lower_hsv, black_upper_hsv = hsv_to_range(black)
    purple_lower_hsv, purple_upper_hsv = hsv_to_range(purple)

    hsv_image = cv2.cvtColor(friend, cv2.COLOR_RGB2HSV)
    blue_mask = cv2.inRange(hsv_image, blue_lower_hsv, blue_upper_hsv)
    yellow_mask = cv2.inRange(hsv_image, yellow_lower_hsv, yellow_upper_hsv)
    green_mask = cv2.inRange(hsv_image, green_lower_hsv, green_upper_hsv)
    red_mask = cv2.inRange(hsv_image, red_lower_hsv, red_upper_hsv)
    black_mask = cv2.inRange(hsv_image, black_lower_hsv, black_upper_hsv)
    purple_mask = cv2.inRange(hsv_image, purple_lower_hsv, purple_upper_hsv)
    
    blue_result = cv2.bitwise_and(friend, friend, mask=blue_mask)
    yellow_result = cv2.bitwise_and(friend, friend, mask=yellow_mask)
    green_result = cv2.bitwise_and(friend, friend, mask=green_mask)
    red_result = cv2.bitwise_and(friend, friend, mask=red_mask)
    black_result = cv2.bitwise_and(friend, friend, mask=black_mask)
    purple_result = cv2.bitwise_and(friend, friend, mask=purple_mask)

    result = cv2.bitwise_or(blue_result, yellow_result)
    result = cv2.bitwise_or(result, green_result)
    result = cv2.bitwise_or(result, red_result)
    result = cv2.bitwise_or(result, black_result)
    result = cv2.bitwise_or(result, purple_result)

    return result


def get_color_mask(friend, color):
    '''
    Returns the color mask of the image
    '''
    lower_hsv, upper_hsv = hsv_to_range(color)
    hsv_image = cv2.cvtColor(friend, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
    blur = cv2.GaussianBlur(mask, (11, 11), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return


def detect_pattern(image, position):
    '''
    Detects if the input image corresponds to the reference figure at the indicated position
    return: bool
    '''
    return 


def show_pattern(code, functions):
    '''
    Displays the pattern to follow on the screen
    '''
    path = "pattern_shapes/img"

    patterns = {}
    for i in range(3):
        img_path = path + str(i) + ".jpg"
        friend = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
        patterns[i] = friend

    for elem in code:
        curr_img = patterns[elem]
        curr_img = functions[elem](curr_img)
        cv2.imshow("Code element 1", curr_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return


def process_pattern_0(img):
    '''
    Processes pattern 0
    '''
    return


def process_pattern_1(img):
    '''
    Processes pattern 1
    '''
    return


def process_pattern_2(img):
    '''
    Processes pattern 2
    '''
    return


def main():    
    # Order of figures to unlock
    PATTERN = [0, 1, 2, 0]

    # Functions to process each pattern
    pattern_functions = {
        0: process_pattern_0,
        1: process_pattern_1,
        2: process_pattern_2
    }
    return


for img_path, friend in patterns.items():
    result = isolate_color(friend)
    plt.imshow(result)
    plt.show()
