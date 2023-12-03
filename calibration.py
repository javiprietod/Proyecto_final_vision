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


def calibrate():
    filenames = list(sorted(glob.glob("imgs/*.jpg")))
    imgs = load_images(filenames)

    # We will execute findChessboardCorners for each image to find the corners
    dim = (9, 5)
    corners = [cv2.findChessboardCorners(i, dim) for i in imgs]

    # OPTIONAL => drawChessboardCorners is a destructive function. so we need to copy corners to avoid data loss
    imgs2 = copy.deepcopy(imgs)

    # Plot each image with the corners in a same figure (only if corners were found)
    fig = plt.figure(figsize=(10, 10))
    for i in range(len(imgs)):
        if corners[i][0]:
            cv2.drawChessboardCorners(imgs2[i], dim, corners[i][1], corners[i][0])
        ax = fig.add_subplot(3, 3, i + 1)
        ax.imshow(imgs2[i])
    plt.show()

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
