import cv2
import numpy as np
from skimage.feature import blob_log


def hsv_to_range(hsv):
    # blue = [219*179//360, 0.93*255, 0.41*255]
    hsv = [hsv[0] * 179 // 360, hsv[1] / 100 * 255, hsv[2] / 100 * 255]
    return np.array([hsv[0] - 10, hsv[1] - 65, hsv[2] - 65]), np.array(
        [hsv[0] + 10, hsv[1] + 65, hsv[2] + 65]
    )


def main():
    img1 = cv2.imread("images_sift/img4_1.png")
    img2 = cv2.imread("images_sift/img4_2.png")
    pattern = cv2.imread("images_sift/pattern4.png")

    # Resize the images to 50% of their original size
    img1 = cv2.resize(img1, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    img2 = cv2.resize(img2, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    pattern = cv2.resize(pattern, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)

    # img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    # img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    blue_hsv = [218, 52, 77]
    low_blue, high_blue = hsv_to_range(blue_hsv)

    hsv1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

    mask1 = cv2.inRange(hsv1, low_blue, high_blue)
    mask2 = cv2.inRange(hsv2, low_blue, high_blue)

    # Blur the mask
    mask1 = cv2.GaussianBlur(mask1, (11, 11), 0)
    mask2 = cv2.GaussianBlur(mask2, (11, 11), 0)

    # Apply a threshold to the frame
    _, threshold1 = cv2.threshold(mask1, 50, 255, cv2.THRESH_BINARY)
    _, threshold2 = cv2.threshold(mask2, 50, 255, cv2.THRESH_BINARY)

    contours1, _ = cv2.findContours(threshold1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours2, _ = cv2.findContours(threshold2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours1 = sorted(contours1, key=cv2.contourArea, reverse=True)
    contours2 = sorted(contours2, key=cv2.contourArea, reverse=True)

    # Approximate a polygon for each contour
    contours1 = cv2.approxPolyDP(contours1[0], 0.01 * cv2.arcLength(contours1[0], True), True)
    contours2 = cv2.approxPolyDP(contours2[0], 0.01 * cv2.arcLength(contours2[0], True), True)
    
    # Draw contours joining the points
    cv2.drawContours(img1, [contours1], -1, (0, 255, 0), 2)
    cv2.drawContours(img2, [contours2], -1, (0, 255, 0), 2)

    # pattern = cv2.cvtColor(pattern, cv2.COLOR_BGR2GRAY)

    # img1 = show_matches(img1, pattern, 1)
    # img2 = show_matches(img2, pattern, 2)

    # img1 = show_blob_matches(img1, pattern)
    # img2 = show_blob_matches(img2, pattern)

    cv2.imshow("Image1", img1)
    cv2.imshow("Image2", img2)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
