import cv2
import numpy as np

DEBUG = True

def removeColors(orig, windowName = None):
    from random import randint
    image = orig.copy()
    colList = [70,100,100]
    print(colList)
    image[np.where((image >= colList).all(axis=2))] = [255,255,255]
    if windowName != None:
        while True:
            cv2.imshow(windowName, image)
            key = cv2.waitKey(0)
            if key == ord(' '): break

            if key == ord('e'):
                colList[0] += 10
            if key == ord('d'):
                colList[0] -= 10

            if key == ord('r'):
                colList[1] += 10
            if key == ord('f'):
                colList[1] -= 10

            if key == ord('t'):
                colList[2] += 10
            if key == ord('g'):
                colList[2] -= 10

            image = orig.copy()
            # colList = [randint(0,255),randint(0,255),randint(0,255)]
            print(colList)
            image[np.where((image >= colList).all(axis=2))] = [255,255,255]


    return image

def edgeDetect(orig, windowName = None):
    if DEBUG: print("getRect.edgeDetect")

    # convert the image to grayscale, blur it, and find edges in the image
    gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
        cv2.THRESH_BINARY,23,8)

    edged = cv2.Canny(thresh, 75, 200)

    if DEBUG:
        if windowName == None: return edged
        cv2.imshow(windowName, thresh)
        cv2.waitKey(0)

    return edged


def findRectContours(image, edged = None):
    if not edged:
        edged = edgeDetect(image)
    if DEBUG: print("getRect.findRectContours")

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    dilated = cv2.dilate(edged, kernel)
    _, contList, _ = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contList = sorted(contList, key = cv2.contourArea, reverse = True)[:5]

    return contList


def cycleContourList(orig, contList, windowName = None):
    if DEBUG: print("getRect.cycleContourList")
    if windowName == None:
        windowName = "cycleContourList"
        cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)

    image = orig.copy()
    cv2.drawContours(image, contList, -1, (0,255,0), 2)

    while True:
        for c in contList:
            temp = image.copy()
            approx = cv2.convexHull(c)
            rect = cv2.minAreaRect(approx)
            box = cv2.boxPoints(rect)
            selectedRect = np.int0(box)
            cv2.drawContours(temp,[selectedRect], 0, (0,0,255), 3)
            # cv2.drawContours(temp, [approx], -1, (0, 255, 0), 2)
            cv2.imshow(windowName, temp)
            key = cv2.waitKey(0)
            if key == ord(' '): return selectedRect


if __name__ == '__main__':
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required = True, help = "Path to the image to be scanned")
    args = vars(ap.parse_args())

    image = cv2.imread(args["image"])
    windowName = "getRect"

    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)

    contours = findRectContours(image)
    selected = cycleContourList(image, contours, windowName)

    cv2.drawContours(image,[selected],0,(0,255,0), 3)
    cv2.imshow(windowName, image)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
