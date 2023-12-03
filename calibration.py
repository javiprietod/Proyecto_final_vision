import cv2
import glob
import copy
import numpy as np
import imageio
import matplotlib.pyplot as plt


def load_images(filenames):
    return [imageio.imread(filename) for filename in filenames]


def get_chessboard_points(chessboard_shape, dx, dy):
    return [
        [(i % chessboard_shape[0]) * dx, (i // chessboard_shape[0]) * dy, 0]
        for i in range(np.prod(chessboard_shape))
    ]


def main():
    filenames = list(sorted(glob.glob("Proyecto_final_vision/imgs/*.jpg")))
    imgs = load_images(filenames)

    # Show images
    plt.figure(figsize=(20, 20))
    for i, img in enumerate(imgs):
        plt.subplot(1, len(imgs), i + 1)
        plt.imshow(img)
        plt.axis("off")
    plt.show()

    # We will execute findChessboardCorners for each image to find the corners
    dim = (9, 5)
    corners = [cv2.findChessboardCorners(i, dim) for i in imgs]

    # OPTIONAL => cornerSubPix is a destructive function. so we need to copy corners to avoid data loss
    corners2 = copy.deepcopy(corners)

    # termination criteria (https://docs.opencv.org/3.1.0/dc/dbb/tutorial_py_calibration.html)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)
    # Cada una de las imagenes la volvemos a blanco y negro
    imgs_grey = [cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) for img in imgs]
    # For each image and corners we are going to use cornerSubPix
    cornersRefined = [
        cv2.cornerSubPix(i, cor[1], dim, (-1, -1), criteria) if cor[0] else []
        for i, cor in zip(imgs_grey, corners2)
    ]

    # OPTIONAL => drawChessboardCorners is a destructive function. so we need to copy corners to avoid data loss
    imgs2 = copy.deepcopy(imgs)

    # Original Image
    plt.figure()
    plt.imshow(imgs2[-1])

    # Image with the corners drawed
    plt.figure()
    plt.imshow(imgs2[1])

    # We are going to retrieve existing corners (cor[0] == True)
    valid_corners = [cor[1] for cor in corners if cor[0]]

    num_valid_images = len(valid_corners)

    # Matrix with the coordinates of the corners
    real_points = get_chessboard_points(dim, 21, 21)

    # We are going to convert our coordinates list in the reference system to numpy array
    object_points = np.asarray(
        [real_points for i in range(num_valid_images)], dtype=np.float32
    )

    # Convert the corners list to array
    image_points = np.asarray(valid_corners, dtype=np.float32)

    # Calibrate
    rms, intrinsics, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        object_points, image_points, imgs[1].shape[0:2], None, None
    )
    # Calculate extrinsecs matrix using Rodigues on each rotation vector addid its translation vector
    extrinsics = list(
        map(lambda rvec, tvec: np.hstack((cv2.Rodrigues(rvec)[0], tvec)), rvecs, tvecs)
    )
    # Save the calibration file
    np.savez("calib_params", intrinsic=intrinsics, extrinsic=extrinsics)

    # Lets print some outputs
    print("Corners standard intrinsics:\n", intrinsics)
    print("Corners standard dist_coefs:\n", dist_coeffs)
    print("root mean sqaure reprojection error:\n", rms)
