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
import re

# Local imports #
from libs.transform import four_point_transform
from libs.calibrate.undistort import undistort
#################

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image to be scanned")
args = vars(ap.parse_args())

cv2.namedWindow("im2", cv2.WINDOW_NORMAL)
cv2.namedWindow("im1", cv2.WINDOW_NORMAL)

def edgeDetect(image):
	print("Edge Detection")

	# load the image and compute the ratio of the old height
	# to the new height, clone it, and resize it

	# convert the image to grayscale, blur it, and find edges in the image
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (5, 5), 0)
	cv2.imshow("im1", blur)

	thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,23,8)
	cv2.imshow("im2", thresh)

	edged = cv2.Canny(thresh, 75, 200)
	cv2.waitKey(0)
	return edged

def selectContour(image, edged):
	print("STEP 1: Select Contour")
	# cv2.imshow("im1", image)
	# cv2.imshow("im2", edged)
	# cv2.waitKey(0)

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

	cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
	cv2.imshow("im1", image)
	cv2.waitKey(0)
	return screenCnt

def transformPerspective(orig, screenCnt):
	print("STEP 3: Apply perspective transform")
	# apply the four point transform to obtain a top-down view of the original image
	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

	cv2.imshow("im2", warped)
	cv2.waitKey(0)
	return warped

def imageOCR(warped):
	print("STEP 4: Run tesseract")

	# cv2.namedWindow("im3", cv2.WINDOW_NORMAL)
	r = cv2.selectROI("im1", warped, True, False)
	cropped = warped[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

	cropped = cv2.cvtColor(cropped,cv2.COLOR_BGR2GRAY)
	thresh = cropped.copy()

	low=39  # 37
	high=13 # 13
	key=0
	while key != ord('s'):

		thresh = cropped.copy()

		bksize = 1
		blur = cv2.GaussianBlur(thresh,(bksize,bksize),0)
		# blur = thresh
		print(low,high)

		_,thresh = cv2.threshold(blur,120,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)


		# low = randint(1,20)*2+1
		# high = randint(0,40)

		dksize = randint(0,2)*2+1
		print("dksize: ", dksize)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(dksize,dksize))
		thresh = cv2.dilate(thresh, kernel)

		cv2.imshow('im1', thresh)
		key = cv2.waitKey(0)


	strs = []
	strs.append(tesser(thresh))

	str = [ line.split("\n") for line in strs ]
	print(str)
	str = list(filter(None, str))
	print(str)
	num = re.compile("\d{3}-\d{3}-\d{3}")
	idNum = list(filter(num.match, str))
	print(idNum)

def tesser(img):
    filename = "img.png"
    cv2.imwrite(filename, img)
    text = pytesseract.image_to_string(Image.open(filename))
    os.remove(filename)
    return text


orig = cv2.imread(args["image"])
orig = undistort(orig)
image = orig.copy()
ratio = image.shape[0] / 500.0
image = imutils.resize(image, height = 500)
cv2.imshow('im1', orig)
cv2.imshow("im2", image)
cv2.waitKey(0)

edged = edgeDetect(image)
cv2.imshow("im1", image)
cv2.imshow("im2", edged)
cv2.waitKey(0)

contour = selectContour(image, edged)
warped = transformPerspective(orig, contour)
imageOCR(warped)
