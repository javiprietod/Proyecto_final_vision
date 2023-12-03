import cv2
import numpy as np
import imageio


def load_images(filenames):
    return [imageio.imread(filename) for filename in filenames]


def hsv_to_range(hsv):
    hsv = [hsv[0]*179//360, hsv[1]/100*255, hsv[2]/100*255]
    return np.array([hsv[0] - 10, hsv[1] - 50, hsv[2] - 50]), np.array([hsv[0] + 10, hsv[1] + 50, hsv[2] + 50])


def isolate_color(friend):
    blue = [220, 80, 40]
    yellow = [45, 100, 70]
    green = [135, 70, 40]
    red = [355, 85, 60]
    purple = [280, 45, 45]

    blue_mask = get_color_mask(friend, blue)
    yellow_mask = get_color_mask(friend, yellow)
    green_mask = get_color_mask(friend, green)
    red_mask = get_color_mask(friend, red)
    purple_mask = get_color_mask(friend, purple)

    # blue_result = cv2.bitwise_and(friend, friend, mask=blue_mask)
    # yellow_result = cv2.bitwise_and(friend, friend, mask=yellow_mask)
    # green_result = cv2.bitwise_and(friend, friend, mask=green_mask)
    # red_result = cv2.bitwise_and(friend, friend, mask=red_mask)
    # purple_result = cv2.bitwise_and(friend, friend, mask=purple_mask)

    # result = cv2.bitwise_or(blue_result, yellow_result)
    # result = cv2.bitwise_or(result, green_result)
    # result = cv2.bitwise_or(result, red_result)
    # result = cv2.bitwise_or(result, purple_result)

    return blue_mask, yellow_mask, green_mask, red_mask, purple_mask


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


def detect_pattern(img, position):
    '''
    Detects if the input image corresponds to the reference figure at the indicated position
    return: img, bool
    '''
    # Functions to process each pattern
    functions = {
        0: process_pattern_0,
        1: process_pattern_1,
        2: process_pattern_2
    }
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img, pattern_check = functions[position](img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img, pattern_check


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
        curr_img, _ = functions[elem](curr_img)
        curr_img = cv2.cvtColor(curr_img, cv2.COLOR_RGB2BGR)
        cv2.imshow("Code element 1", curr_img)
        cv2.waitKey(1500)
    cv2.destroyAllWindows()
    return


def process_pattern_0(img):
    '''
    Processes pattern 0
    '''
    blue_mask, yellow_mask, green_mask, red_mask, purple_mask = isolate_color(img)

    # Red_mask and purple_mask should not have big contours
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(red_contours) > 0:
        for contour in red_contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 100 or h > 100:
                return img, False
    if len(purple_contours) > 0:
        for contour in purple_contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 100 or h > 100:
                return img, False

    bboxes = []
    bboxes_centers = []

    # Detect blue
    blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(blue_contours) < 2:
        return img, False
    blue_contours = sorted(blue_contours, key=cv2.contourArea, reverse=True)
    for i in range(2):
        x, y, w, h = cv2.boundingRect(blue_contours[i])
        bboxes.append((x, y, w, h))
        bboxes_centers.append((x + w//2, y + h//2))
    
    # Detect yellow
    yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(yellow_contours) < 1:
        return img, False
    yellow_contours = sorted(yellow_contours, key=cv2.contourArea, reverse=True)
    x, y, w, h = cv2.boundingRect(yellow_contours[0])
    bboxes.append((x, y, w, h))
    bboxes_centers.append((x + w//2, y + h//2))

    # Detect green
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(green_contours) < 1:
        return img, False
    green_contours = sorted(green_contours, key=cv2.contourArea, reverse=True)
    x, y, w, h = cv2.boundingRect(green_contours[0])
    bboxes.append((x, y, w, h))
    bboxes_centers.append((x + w//2, y + h//2))

    # Center of bboxes_centers
    x_center = sum([i[0] for i in bboxes_centers]) // len(bboxes_centers)
    y_center = sum([i[1] for i in bboxes_centers]) // len(bboxes_centers)
    
    # First pattern has 4 elements: 1 blue upperleft, 1 green upperright, 1 yellow bottomleft and 1 blue bottomright
    # So, we can see from the center if the pattern is correct
    # For this, we will inspect each bbox_center and see if it is in the correct position
    upperleft, upperright, bottomleft, bottomright = False, False, False, False
    for idx, center in enumerate(bboxes_centers):
        if center[0] < x_center and center[1] < y_center:
            if idx <= 1:
                upperleft = True
        elif center[0] > x_center and center[1] < y_center:
            if idx == 3:
                upperright = True
        elif center[0] < x_center and center[1] > y_center:
            if idx == 2:
                bottomleft = True
        elif center[0] > x_center and center[1] > y_center:
            if idx <= 1:
                bottomright = True

    pattern_check = upperleft == upperright == bottomleft == bottomright == True
    if pattern_check:
        bbox_color = (0, 255, 0)
    else:
        bbox_color = (255, 0, 0)
    
    for bbox in bboxes:
        x, y, w, h = bbox
        cv2.rectangle(img, (x, y), (x + w, y + h), bbox_color, 2)

    return img, pattern_check


def process_pattern_1(img):
    '''
    Processes pattern 1
    '''
    blue_mask, yellow_mask, green_mask, red_mask, purple_mask = isolate_color(img)

    # Purple_mask should not have big contours
    purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(purple_contours) > 0:
        for contour in purple_contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 100 or h > 100:
                return img, False
    
    bboxes = []
    bboxes_centers = []

    # Detect blue
    blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(blue_contours) < 2:
        return img, False
    blue_contours = sorted(blue_contours, key=cv2.contourArea, reverse=True)
    for i in range(2):
        x, y, w, h = cv2.boundingRect(blue_contours[i])
        bboxes.append((x, y, w, h))
        bboxes_centers.append((x + w//2, y + h//2))
    
    # Detect yellow
    yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(yellow_contours) < 1:
        return img, False
    yellow_contours = sorted(yellow_contours, key=cv2.contourArea, reverse=True)
    x, y, w, h = cv2.boundingRect(yellow_contours[0])
    bboxes.append((x, y, w, h))
    bboxes_centers.append((x + w//2, y + h//2))

    # Detect green
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(green_contours) < 1:
        return img, False
    green_contours = sorted(green_contours, key=cv2.contourArea, reverse=True)
    x, y, w, h = cv2.boundingRect(green_contours[0])
    bboxes.append((x, y, w, h))
    bboxes_centers.append((x + w//2, y + h//2))

    # Center of bboxes_centers
    x_center = sum([i[0] for i in bboxes_centers]) // len(bboxes_centers)
    y_center = sum([i[1] for i in bboxes_centers]) // len(bboxes_centers)

    # Detect red
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(red_contours) < 1:
        return img, False
    red_contours = sorted(red_contours, key=cv2.contourArea, reverse=True)
    x, y, w, h = cv2.boundingRect(red_contours[0])
    bboxes.append((x, y, w, h))
    bboxes_centers.append((x + w//2, y + h//2))

    # First, we determine if red_center is the closest to (x_center, y_center)
    dist_to_center = get_distance((x_center, y_center), bboxes_centers[-1])
    for center in bboxes_centers[:-1]:
        if get_distance((x_center, y_center), center) < dist_to_center:
            return img, False
    
    # Now, the rest of the pattern has 4 elements: 1 blue upperleft, 1 green upperright, 1 yellow bottomleft
    # and 1 blue bottomright
    # So, we can see from the center if the pattern is correct
    # For this, we will inspect each bbox_center and see if it is in the correct position
    upperleft, upperright, bottomleft, bottomright = False, False, False, False
    for idx, center in enumerate(bboxes_centers):
        if center[0] < x_center and center[1] < y_center:
            if idx <= 1:
                upperleft = True
        elif center[0] > x_center and center[1] < y_center:
            if idx == 3:
                upperright = True
        elif center[0] < x_center and center[1] > y_center:
            if idx == 2:
                bottomleft = True
        elif center[0] > x_center and center[1] > y_center:
            if idx <= 1:
                bottomright = True

    pattern_check = upperleft == upperright == bottomleft == bottomright == True
    if pattern_check:
        bbox_color = (0, 255, 0)
    else:
        bbox_color = (255, 0, 0)
    
    for bbox in bboxes:
        x, y, w, h = bbox
        cv2.rectangle(img, (x, y), (x + w, y + h), bbox_color, 2)

    return img, pattern_check


def get_distance(point1, point2):
    '''
    Returns the distance between point1 and point2
    '''
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5


def process_pattern_2(img):
    '''
    Processes pattern 2
    '''
    _, _, _, _, purple_mask = isolate_color(img)

    # Detect purple
    purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(purple_contours) < 1:
        return img, False
    purple_contours = sorted(purple_contours, key=cv2.contourArea, reverse=True)
    poly = cv2.approxPolyDP(purple_contours[0], 0.01*cv2.arcLength(purple_contours[0], True), True)
    if len(poly) < 12:
        return img, False
    cv2.drawContours(img, [poly], 0, (0, 255, 0), 2)

    return img, True


def password(PATTERN):
    '''
    Shows the pattern to follow
    '''

    # Functions to process each pattern
    pattern_functions = {
        0: process_pattern_0,
        1: process_pattern_1,
        2: process_pattern_2
    }

    show_pattern(PATTERN, pattern_functions)
    return
