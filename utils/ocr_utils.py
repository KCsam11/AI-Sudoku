import cv2
import numpy as np
import operator
from skimage.segmentation import clear_border
import imutils

def preprocessing(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    proc = cv2.GaussianBlur(gray.copy(), (9, 9), 0) 
    proc = cv2.adaptiveThreshold(proc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    proc = cv2.bitwise_not(proc, proc)   
    noyau = np.array([[0., 1., 0.], [1., 1., 1.], [0., 1., 0.]],np.uint8) 
    proc = cv2.dilate(proc, noyau)

    return {
        "binary_image": proc,
        "gray_image": gray
    }

def get_contours(prep):
    contours, h = cv2.findContours(prep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    if not contours:
        raise ValueError("Aucun contour trouvé dans l'image.")
    
    contours = sorted(contours, key=cv2.contourArea, reverse=True) 
    polygon = contours[0]
    bottom_right, _ = max(enumerate([pt[0][0] + pt[0][1] for pt in
                      polygon]), key=operator.itemgetter(1))
    top_left, _ = min(enumerate([pt[0][0] + pt[0][1] for pt in
                    polygon]), key=operator.itemgetter(1))
    bottom_left, _ = min(enumerate([pt[0][0] - pt[0][1] for pt in
                        polygon]), key=operator.itemgetter(1))
    top_right, _ = max(enumerate([pt[0][0] - pt[0][1] for pt in
                    polygon]), key=operator.itemgetter(1))
    
    return [polygon[top_left][0], polygon[top_right][0], polygon[bottom_right][0], polygon[bottom_left][0]]

def perspective_transform(img, corners):
    top_left, top_right, bottom_right, bottom_left = corners
    width = max([top_right[0] - top_left[0], bottom_right[0] - bottom_left[0]])
    height = max(bottom_left[1] - top_left[1], bottom_right[1] - top_right[1])
    dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], np.float32)
    M = cv2.getPerspectiveTransform(np.array(corners, np.float32), dst)

    return cv2.warpPerspective(img, M, (width, height))


def get_cell(img):
    squares = [] 
    side_col = img.shape[1] 
    side_row = img.shape[0]
    side_row = side_row / 9
    side_col = side_col / 9
    for j in range(9):
        for i in range(9):
            p1 = (int(i * side_col), int(j * side_row)) 
            p2 = (int((i+1) * side_col), int((j+1) * side_row))
            squares.append((p1, p2)) 

    return squares

def get_digits(img, allCell):
    digits = []
    for cell in allCell:
        digit = extract_digit(img,cell)
        digits.append(digit)
    return digits

def cut_from_rect(img, rect):
    (x1, y1), (x2, y2) = rect
    return img[y1:y2, x1:x2]

def extract_digit(img ,cell, debug=False):
    binary_cell = cut_from_rect(img,cell)
    thresh = cv2.threshold(binary_cell, 0, 255,
	    cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    thresh = clear_border(thresh)

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if len(cnts) == 0:
        return None
	
    c = max(cnts, key=cv2.contourArea)
    mask = np.zeros(thresh.shape, dtype="uint8")
    cv2.drawContours(mask, [c], -1, 255, -1)
   
    (h, w) = thresh.shape
    percentFilled = cv2.countNonZero(mask) / float(w * h)
	
    if percentFilled < 0.03:
        return None
    digit = cv2.bitwise_and(thresh, thresh, mask=mask)

    return digit
