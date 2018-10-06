# scan3.py
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import imutils

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,help="path to input image to be OCR'd")
args = vars(ap.parse_args())

cv2.namedWindow('image',cv2.WINDOW_NORMAL)

image = cv2.imread(args["image"])
gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray,(1,1),0)

thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,33,7)
thresh2 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,19,10)
thresh3 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,65,15)
cv2.imshow('image', thresh)
cv2.waitKey(0)
cv2.imshow('image', thresh2)
cv2.waitKey(0)
cv2.imshow('image', thresh3)
cv2.waitKey(0)
# # cv::bitwise_not(img, img);

_,contours,hierarchy = cv2.findContours(thresh, 1, 2)
cnt = contours[0]
epsilon = 0.1*cv2.arcLength(cnt,True)
approx = cv2.approxPolyDP(cnt,epsilon,True)
out = cv2.drawContours(thresh, [approx], -1, (0,255,0), 3)
cv2.imshow('image', out)
cv2.waitKey(0)
