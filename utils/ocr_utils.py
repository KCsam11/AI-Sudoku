#reconnaissance sudoku
import cv2
import numpy as np

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

def perspective_transform(prep_img, contours):

def get_cell(binary_img):

def get_digit(gray_img_perspective,all_cells,size,debug=False):

def extract_digit(img,cell_cord,size):

