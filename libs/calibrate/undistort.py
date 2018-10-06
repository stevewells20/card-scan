# You should replace these 3 lines with the output in calibration step
import sys
import cv2
assert cv2.__version__[0] == '3', 'The fisheye module requires opencv version >= 3.0.0'
import numpy as np

DIM=(2592, 1944)
K=np.array([[2929.9647197520762, 0.0, 1201.0452119753963], [0.0, 2942.994096836105, 991.3995486616822], [0.0, 0.0, 1.0]])
D=np.array([[-0.08029996518583886], [-0.9182134271668104], [7.613032253015024], [-18.05792982013352]])

def undistort_path(img_path):
    img = cv2.imread(img_path)
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    cv2.namedWindow("undistorted", cv2.WINDOW_NORMAL)
    cv2.imshow("undistorted", undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def undistort(img):
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    # cv2.namedWindow("undistorted", cv2.WINDOW_NORMAL)
    # cv2.imshow("undistorted", undistorted_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return undistorted_img

if __name__ == '__main__':
    for p in sys.argv[1:]:
        undistort(p)
