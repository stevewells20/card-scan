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

refPt = []
dragging = False

def get_mouse_xy(event, x, y, flags, param):
	# grab references to the global variables
	global refPt, dragging

	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that dragging is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		dragging = True
	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP:
		# record the ending (x, y) coordinates and indicate that
		# the dragging operation is finished
		refPt.append((x, y))
		dragging = False
		# draw a rectangle around the region of interest
		cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.imshow("image", image)

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
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
dilated = cv2.dilate(edged, kernel)
_, cnts, _ = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

key = 0
while key != ord('s'):
	for c in cnts:
		temp = image.copy()
		approx = cv2.convexHull(c)
		rect = cv2.minAreaRect(approx)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		screenCnt = box
		cv2.drawContours(temp,[box],0,(0,0,255),2)
		cv2.drawContours(temp, [approx], -1, (0, 255, 0), 2)
		cv2.imshow('im1', temp)
		key = cv2.waitKey(0)
		if key == ord('s'): break

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

# key = 0
# gray = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
#
# while key != ord('q'):
#     arg2 = randint(90,100)
#     # if arg2 % 2 == 0: arg2 += 1
#     arg3 = randint(240,255)
#     print(arg2, arg3)

key=0
low_thresh=100
high_thresh=247
while key != ord('s'):

	thresh = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
	thresh = cv2.threshold(thresh,low_thresh, high_thresh, cv2.THRESH_BINARY)[1]
	low_thresh = randint(0,255)
	high_thresh = randint(0,255)
	thresh = cv2.medianBlur(thresh, 3)

	cv2.setMouseCallback("im2",get_mouse_xy,thresh)	#binds the screen,function and image
	cv2.imshow('im2', thresh)
	key = cv2.waitKey(0)

# warped = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
# warped = cv2.threshold(warped,140, 255,cv2.THRESH_BINARY)[1]
# warped = cv2.medianBlur(warped, 3)

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
# Copy ROI's to new img mats
nameImg = thresh[name['y1']:name['y2'], name['x1']:name['x2']]
statusImg = thresh[status['y1']:status['y2'], status['x1']:status['x2']]
numImg = thresh[num['y1']:num['y2'], num['x1']:num['x2']]

while key != ord('s'):
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

strs = []
for img in (nameImg, statusImg, numImg):
    strs.append(tesser(img))

print(strs)
