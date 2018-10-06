from PIL import Image
import pytesseract
import argparse
import cv2
import os
import imutils
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,help="path to input image to be OCR'd")
args = vars(ap.parse_args())

im = cv2.imread(args["image"])
gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray,(1,1),1000)
flag, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)
cv2.namedWindow('image',cv2.WINDOW_NORMAL)
# cv2.imshow('image', im)
# cv2.waitKey(0)
# cv2.imshow('image', gray)
# cv2.waitKey(0)
# cv2.imshow('image', blur)
# cv2.waitKey(0)

_, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea,reverse=True)[0]
