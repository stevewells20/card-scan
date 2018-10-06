# import the necessary packages
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils
from PIL import Image
import pytesseract
import os
from random import randint

# Local imports #
from pyimagesearch.transform import four_point_transform
from pyimagesearch.calib.undistort import undistort
#################

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
	help = "Path to the image to be scanned")
args = vars(ap.parse_args())

cv2.namedWindow("im1", cv2.WINDOW_NORMAL)
cv2.namedWindow("im2", cv2.WINDOW_NORMAL)

def get_mouse_xy(event,x,y,flags,param):
	if event==cv2.EVENT_LBUTTONDBLCLK:		# here event is left mouse button double-clicked
		print(x,y)

print("STEP 0: Image Acquisition and Preparation")

# load the image and compute the ratio of the old height
# to the new height, clone it, and resize it
image = cv2.imread(args["image"])
cv2.imshow("im1", image)
image = undistort(image)
cv2.imshow("im2", image)
cv2.waitKey(0)
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height = 500)


# convert the image to grayscale, blur it, and find edges in the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,5,30)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
cv2.imshow("im1", blur)

thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,23,8)
cv2.imshow("im2", thresh)

print(cv2.mean(thresh))

edged = cv2.Canny(thresh, 75, 200)
cv2.waitKey(0)
# key = 0
# while key != ord('q'):
#     arg2 = randint(22,25)
#     if arg2 % 2 == 0: arg2 += 1
#     arg3 = randint(5,10)
#     print(arg2, arg3)
#     # _,thresh = cv2.threshold(blur, arg2, arg3, cv2.THRESH_BINARY)
#     thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,arg2,arg3)
#     edged = cv2.Canny(thresh, 75, 200)
#     cv2.imshow("im", thresh)
#     cv2.imshow("edge", edged)
#     key = cv2.waitKey(0)
# cv2.destroyAllWindows()

# show the original image and the edge detected image
print("STEP 1: Edge Detection")
cv2.imshow("im1", image)
cv2.imshow("im2", edged)
cv2.waitKey(0)

# find the contours in the edged image, keeping only the
# largest ones, and initialize the screen contour
_img,cnts, heirarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
# cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = cnts[0] if imutils.is_cv2() else cnts[1]
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

# loop over the contours
temp = image.copy()
# cv2.drawContours(temp, cnts, -1, (0, 255, 0), 2)
# cv2.imshow('im1', temp)
# cv2.waitKey(0)
for c in cnts:
	# approximate the contour
	peri = cv2.arcLength(c, True)
    # the second param should be between 1% - 5%
	approx = cv2.approxPolyDP(c, 0.10 * peri, True)
	# approx = cv2.convexHull(c)
	cv2.drawContours(temp, [approx], -1, (0, 255, 0), 2)
	cv2.imshow('im1', temp)
	cv2.waitKey(0)
	# if our approximated contour has four points, then we can assume that we have found our screen
	if len(approx) == 4:
		screenCnt = approx
		break

# show the contour (outline) of the piece of paper
print("STEP 2: Find contours of paper")
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
cv2.imshow("im1", image)
cv2.waitKey(0)

print("STEP 3: Apply perspective transform")
# apply the four point transform to obtain a top-down view of the original image
warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

# convert the warped image to grayscale, then threshold it
# to give it that 'black and white' paper effect
# warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

# T = threshold_local(warped, 11, offset = 10, method = "gaussian")
# warped = (warped > T).astype("uint8") * 255

cv2.imshow("im2", warped)
cv2.waitKey(0)

print("STEP 4: Run tesseract")

# key = 0
# gray = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
#
# while key != ord('q'):
#     arg2 = randint(2,30)
#     if arg2 % 2 == 0: arg2 += 1
#     arg3 = randint(0,25)
#     print(arg2, arg3)
#     # _,thresh = cv2.threshold(blur, arg2, arg3, cv2.THRESH_BINARY)
#     thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,arg2,arg3)
#
#     cv2.setMouseCallback("im",get_mouse_xy,warped)	#binds the screen,function and image
#     cv2.imshow('im', warped)
#     cv2.setMouseCallback("edge", get_mouse_xy, thresh)
#     cv2.imshow('edge', thresh)
#     key = cv2.waitKey(0)

strs = []
# Location ROI
name = {
    'x1': 1100,
    'y1': 714,
    'x2': 1930,
    'y2': 900
}
# Status ROI
status = {
    'x1': 1500,
    'y1': 900,
    'x2': 1930,
    'y2': 1050
}
# Student Number ROI
num = {
    'x1': 1380,
    'y1': 1030,
    'x2': 1930,
    'y2': 1160
}

# key = 0
# gray = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
#
# while key != ord('q'):
#     arg2 = randint(90,100)
#     # if arg2 % 2 == 0: arg2 += 1
#     arg3 = randint(240,255)
#     print(arg2, arg3)

thresh = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(thresh,100, 247, cv2.THRESH_BINARY)[1]
thresh = cv2.medianBlur(thresh, 3)

cv2.setMouseCallback("im2",get_mouse_xy,thresh)	#binds the screen,function and image
cv2.imshow('im2', thresh)
key = cv2.waitKey(0)

# warped = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
# warped = cv2.threshold(warped,140, 255,cv2.THRESH_BINARY)[1]
# warped = cv2.medianBlur(warped, 3)

# Copy ROI's to new img mats
nameImg = thresh[name['y1']:name['y2'], name['x1']:name['x2']]
statusImg = thresh[status['y1']:status['y2'], status['x1']:status['x2']]
numImg = thresh[num['y1']:num['y2'], num['x1']:num['x2']]

cv2.imshow('nameImg', nameImg)
# cv2.waitKey(0)
cv2.imshow('statusImg', statusImg)
# cv2.waitKey(0)
cv2.imshow('numImg', numImg)
cv2.waitKey(0)

def tesser(img):
    filename = "img.png"
    cv2.imwrite(filename, img)
    text = pytesseract.image_to_string(Image.open(filename))
    os.remove(filename)
    return text

for img in (nameImg, statusImg, numImg):
    strs.append(tesser(img))

print(strs)
