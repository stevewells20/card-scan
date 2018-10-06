from __future__ import print_function
import cv2 as cv
import argparse
max_lowThreshold = 100
window_name = 'Edge Map'
title_trackbar = 'Min Threshold:'
ratio = 4
kernel_size = 3
low_threshold = 100

def CannyThreshold(val):
    low_threshold = val
    img_blur = cv.blur(src_gray, (3,3))
    detected_edges = cv.Canny(img_blur, low_threshold, low_threshold*ratio, kernel_size)
    mask = detected_edges != 0
    dst = src * (mask[:,:,None].astype(src.dtype))
    cv.imshow(window_name, dst)

def Ratio(val):
    ratio = val
    CannyThreshold(low_threshold)

parser = argparse.ArgumentParser(description='Code for Canny Edge Detector tutorial.')
parser.add_argument('--input', '-i', help='Path to input image.', default='./pictures/2.jpg')
args = parser.parse_args()
src = cv.imread(args.input)
if src is None:
    print('Could not open or find the image: ', args.input)
    exit(0)

src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
cv.namedWindow(window_name, cv.WINDOW_NORMAL)
cv.createTrackbar("low thresh", window_name , 0, max_lowThreshold, CannyThreshold)
cv.createTrackbar("ratio", window_name , 0, max_lowThreshold, Ratio)
CannyThreshold(0)
cv.waitKey()
