import cv2
import operator
import numpy as np

marge = 4
cell = 28 + 2 * marge
taille_grille = cell * 9
flag = 0

# Preprocess the image
def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9, 2)
    return thresh

# Get the grid contour
def get_contours(thresh):
    contour_grille = None
    area_max = 0

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        area = cv2.contourArea(c)
        if area > 25000:
            peri = cv2.arcLength(c, True)
            polygone= cv2.approxPolyDP(c, 0.01 * peri, True)
            if area > area_max and len(polygone) == 4:
                contour_grille = polygone
                area_max = area
    return contour_grille


# Get corners of the grid
def get_corners(contour_grille):
    if contour_grille is not None:
     points = np.vstack(contour_grille).squeeze()
     points = sorted(points, key=operator.itemgetter(1))
     if points[0][0] < points[1][0]:
         if points[3][0] < points[2][0]:
            pts1 = np.float32([points[0], points[1], points[3], points[2]])
         else:
            pts1 = np.float32([points[0], points[1], points[2], points[3]])
     else:
         if points[3][0] < points[2][0]:
            pts1 = np.float32([points[1], points[0], points[3], points[2]])
         else:
            pts1 = np.float32([points[0], points[1], points[2], points[3]])

     pts2 = np.float32([[0, 0], [taille_grille, 0], [0, taille_grille], [
                          taille_grille, taille_grille]])
    return pts1, pts2

# Get the perspective of the grid
def perspective(pts1, pts2, img):
    M = cv2.getPerspectiveTransform(pts1, pts2)
    grille = cv2.warpPerspective(img, M, (taille_grille, taille_grille))
    grille = cv2.cvtColor(grille, cv2.COLOR_BGR2GRAY)
    grille = cv2.adaptiveThreshold(grille, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 7, 3) 
    return grille   

# Aplly OCR to the grid
def ocr_sudoku(model,grille):
    if flag ==0:
        grille_txt = []
        for y in range(9):
            ligne = ""
            for x in range(9):
                ymin = y * cell + marge
                ymax = (y + 1) * cell - marge
                xmin = x * cell + marge
                xmax = (x + 1) * cell - marge
                img_cell = grille[ymin:ymax, xmin:xmax]
                x = img_cell.reshape(1, 28, 28, 1)
                if x.sum() > 10000:
                    prediction = np.argmax(model.predict(x), axis=-1)
                    ligne += "{:d}".format(prediction[0])
                else:
                    ligne += "{:d}".format(0)
            grille_txt.append(ligne)
    return grille_txt