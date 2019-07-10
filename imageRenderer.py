import cv2
import numpy as np

import utils.colormaps as cm
from gol import GoL


class RenderSettings:
    def __init__(self, width, height):
        # Image Size
        self.width = width
        self.height = height

        # Color Stuff
        self.colormap = cm.COLORMAP_BLACK_WHITE
        self.offColorIndex = 0
        self.onColorIndex = 255

        # Position
        self.topLeft = (0, 0)
        self.bottomRight = (-1, -1)

        # Visual Settings
        self.showNeighbours = False
        self.showGridlines = False

        # Extras
        self.highlights = []
        self.texts = []


def renderImage(gol: GoL, settings: RenderSettings):
    h = settings.height
    w = settings.width
    img = np.zeros((h, w), dtype="B")

    xMin, yMin = settings.topLeft
    xMax, yMax = settings.bottomRight
    if xMax < 0:
        xMax += gol.width
    if yMax < 0:
        yMax += gol.height

    scaling = min(w / (xMax - xMin + 1), h / (yMax - yMin + 1))

    xOffset = int((xMin - int(xMin) - 1) * scaling)
    yOffset = int((yMin - int(yMin) - 1) * scaling)

    font = cv2.FONT_HERSHEY_PLAIN
    textScaling = 0.05
    if settings.showNeighbours:
        while max(cv2.getTextSize("0", font, textScaling, 1)[0]) < scaling * 0.9:
            textScaling += 0.05

    lastX = xOffset
    for x in range(int(xMin), int(xMax + 1) + 1):
        nextX = int((x + 1 - xMin) * scaling)
        lastY = yOffset
        for y in range(int(yMin), int(yMax + 1) + 1):
            nextY = int((y + 1 - yMin) * scaling)

            try:
                grayValue = settings.onColorIndex if gol.getXY(x, y) else settings.offColorIndex
            except:
                grayValue = settings.offColorIndex
            if settings.showGridlines:
                cv2.rectangle(img, (lastX, lastY), (nextX, nextY), 255, 2)

            cv2.rectangle(img, (lastX, lastY), (nextX, nextY), grayValue, -1)
            lastY = nextY

            if settings.showNeighbours:
                nb = gol.countNeighbours(x, y)
                if nb == 0:
                    continue
                textColor = [255 - grayValue for _ in range(3)]
                actualNeighbours = nb - gol.getXY(x, y)
                cv2.putText(img, str(actualNeighbours), (int(lastX + 0.05 * scaling), int(lastY - 0.05 * scaling)),
                            font, textScaling, textColor, 1,
                            cv2.LINE_AA)
        lastX = nextX

    coloredImg = cm.colorize(img, settings.colormap)
    for position, text, color in settings.texts:
        tmp1, tmp2 = position
        x = int((tmp1 - xMin + 0.05) * scaling)
        y = int((tmp2 - yMin + 0.95) * scaling)
        cv2.putText(coloredImg, text, (x, y),
                    font, textScaling, color, 1,
                    cv2.LINE_AA)

    for position, color, size in settings.highlights:
        tmp1, tmp2 = position
        try:
            x1, y1 = tmp1
            x2, y2 = tmp2
            x1 = int((x1 - xMin) * scaling)
            y1 = int((y1 - yMin) * scaling)
            x2 = int((x2 - xMin) * scaling)
            y2 = int((y2 - yMin) * scaling)
        except:
            x1 = int((tmp1 - xMin) * scaling)
            y1 = int((tmp2 - yMin) * scaling)
            x2 = int((tmp1 + 1 - xMin) * scaling)
            y2 = int((tmp2 + 1 - yMin) * scaling)
        cv2.rectangle(coloredImg, (x1, y1), (x2, y2), color, size)
    return coloredImg


def fastImage(gol: GoL, settings: RenderSettings):
    img = np.transpose(gol.board * 255).astype("B")
    img = img[int(settings.topLeft[0]):int(settings.bottomRight[0]), int(settings.topLeft[1]):int(settings.bottomRight[1])]
    if settings.colormap is not None:
        img = cm.colorize(img, settings.colormap)

    return img
