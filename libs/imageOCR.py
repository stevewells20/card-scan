import pytesseract
from PIL import Image
import os
import cv2
import numpy as np
from random import randint
import re

DEBUG = True

def extractText(warped, windowName = None):
    if DEBUG: print("imageOCR.extractText")
    if windowName == None:
        windowName = "extractText"
        cv2.namedWindow(windowName, WINDOW_NORMAL)

    sizeY, sizeX, numChann = warped.shape
    defaultROI = (int(sizeX/5*3), int(sizeY/5*3), sizeX, sizeY)
    print(defaultROI)
    # defaultROI = (1201, 725, 746, 488)
    roiCopy = warped.copy()
    cv2.rectangle(roiCopy, (defaultROI[0],defaultROI[1]), \
        (defaultROI[2],defaultROI[3]), (0,0,255),2)
    r = cv2.selectROI(windowName, roiCopy, True, False)
    if r == (0,0,0,0): r = defaultROI
    print(r)
    cropped = warped[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

    cropped = cv2.cvtColor(cropped,cv2.COLOR_BGR2GRAY)
    thresh = cropped.copy()

    low=39  # 37
    high=13 # 13
    key=0
    while key != ord(' '):

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

        cv2.imshow(windowName, thresh)
        key = cv2.waitKey(0)

    strs = (tesserRead(thresh))

    return strs

def verifyIDCard(text):
    strList = text.split("\n")
    print(strList)
    strList = list(filter(None, strList))

    ########## Testing Block
    # re.match("|".join([regex_str1, regex_str2, regex_str2]), line)

    hyph = re.compile(r"—|--|_|~")
    comma = re.compile(r"\.|'|`")
    empty = re.compile(r"!|‘|\||=| (?=\d+)|\"|“|\W,")
    space = re.compile(r" {2,}|(?<=,)(?=\w)")
    doubleU = re.compile(r"VV|vv")
    lowcaseL = re.compile(r"(?<!^)I")
    doubleL = re.compile(r"(?<!^)H|vv")
    strList = [ re.sub(hyph, "-", item) for item in strList ]
    strList = [ re.sub(comma, ",", item) for item in strList ]
    strList = [ re.sub(space, " ", item) for item in strList ]
    strList = [ re.sub(empty, "", item) for item in strList ]
    strList = [ re.sub(doubleU, "W", item) for item in strList ]
    strList = [ re.sub(doubleL, "ll", item) for item in strList ]
    strList = [ re.sub(lowcaseL, "l", item) for item in strList ]
    print(strList)
    ##########

    name = re.compile("[A-Z][a-z]+,\s*\w+\s?\w?")#,\s?\b\w+\b\s\b\w+")
    fullName = list(filter(name.match, strList.copy()))
    print(fullName)
    num = re.compile("\d{3}-\d{3}-\d{3}")
    idNum = list(filter(num.search, strList.copy()))
    print(idNum)
    return [ fullName[0], idNum[0] ]

def tesserRead(img, saveName = "img.png"):
    filename = "img.png"
    cv2.imwrite(saveName, img)
    text = pytesseract.image_to_string(Image.open(saveName))
    os.remove(saveName)
    return text

if __name__ == '__main__':
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required = False, help = "Path to the image to be scanned")
    ap.add_argument("-t", "--text", required = False, help = "ID Card text to validate")
    args = vars(ap.parse_args())

    if args["text"] != None:
        print(verifyIDCard(args["text"]))

    if args["image"] != None:
        image = cv2.imread(args["image"])
        windowName = "imageOCR"

        cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)

        extracted = extractText(image, windowName)
        # print(extracted)
        verified = verifyIDCard(extracted)
        print(verified)

    cv2.destroyAllWindows()
