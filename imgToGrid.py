import cv2
import numpy as np


def toGrid(img:np.ndarray, size=None, threshold=128):
    if size is not None:
        img = cv2.resize(img, size)
    winName = "ScaledImage"
    cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
    k = 5
    cv2.imshow(winName, img)
    cv2.resizeWindow(winName, 192*k, 108*k)
    w, h = img.shape
    grid = [[1-(img[x][y] >= threshold) for x in range(w)] for y in range(h)]
    return grid


def readImage(path):
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)

def pathToGrid(path, size=None,threshold=128):
    img = readImage(path)
    if img is None:
        raise ValueError("Cannot read image")
    return toGrid(img, size, threshold)

if __name__ == '__main__':
    path = "data/imgs/gol.png"
    img = readImage(path)
    grid = toGrid(img, (100,100))
    print(grid)
