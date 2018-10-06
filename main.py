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
from libs.getRect import findRectContours, cycleContourList, removeColors
from libs.imageOCR import extractText, verifyIDCard
#################

def transformPerspective(orig, screenCnt):
	print("STEP 3: Apply perspective transform")
	# apply the four point transform to obtain a top-down view of the original image
	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

	cv2.imshow("im2", warped)
	cv2.waitKey(0)
	return warped

DEBUG = True

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image to be scanned")
args = vars(ap.parse_args())

cv2.namedWindow("im2", cv2.WINDOW_NORMAL)
cv2.namedWindow("im1", cv2.WINDOW_NORMAL)

orig = cv2.imread(args["image"])
orig = undistort(orig)
image = orig.copy()
ratio = image.shape[0] / 500.0
image = imutils.resize(image, height = 500)
cv2.imshow('im1', orig)
cv2.imshow("im2", image)
cv2.waitKey(0)

contourList = findRectContours(image)
contour = cycleContourList(image, contourList, 'im1')
warped = transformPerspective(orig, contour)
warped = removeColors(warped, 'im1')
extracted = extractText(warped, 'im1')
print(extracted)
verified = verifyIDCard(extracted)
print(verified)

cv2.destroyAllWindows()
