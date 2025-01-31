#reconnaissance sudoku
import cv2
import numpy as np
import operator


def prepocessing(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    proc = cv2.GaussianBlur(gray.copy(), (9, 9), 0) 
    proc = cv2.adaptiveThreshold(proc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    proc = cv2.bitwise_not(proc, proc)   
    noyau = np.array([[0., 1., 0.], [1., 1., 1.], [0., 1., 0.]],np.uint8) 
    proc = cv2.dilate(proc, noyau)

    return {
        "gray_image": gray,
        "binary_image": proc,
    }

def get_contours(prep_img):  
    contours, _ = cv2.findContours(prep_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
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

def perspective_transform(prep_img, contours):
    top_left, top_right, bottom_right, bottom_left = contours
    width = max([top_right[0] - top_left[0], bottom_right[0] - bottom_left[0]])
    height = max(bottom_left[1] - top_left[1], bottom_right[1] - top_right[1])
    dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], np.float32)
    M = cv2.getPerspectiveTransform(np.array(contours, np.float32), dst)

    return cv2.warpPerspective(prep_img, M, (width, height))


def get_cell(binary_img):

def get_digit(gray_img_perspective,all_cells,size,debug=False):

def extract_digit(img,cell_cord,size):

