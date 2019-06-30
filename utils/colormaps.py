import random

import cv2
import numpy as np

COLORS_DARK = ["1771F1", "298A08", "FF6B00", "E20338", "761CEA"]
COLORS_PASTELL = ['7777DD', '77DDDD', 'DD7777', 'DDDD77', '77DD77', 'DD77DD']
COLORS_BASE = ['FF0000', 'FFFF00', '00FF00', '00FFFF', 'FF00FF', '0000FF']
COLORS_BLACK_WHITE = ['000000', 'FFFFFF']


def colorblock(color):
    return np.full((256, 256, 3), color, dtype="B")


def colorize(img, colormap=None):
    if colormap is None:
        return img
    if callable(colormap):
        colormap = colormap()
    channels = [cv2.LUT(img, colormap[:, i]) for i in range(3)]
    return np.dstack(channels)


def _htmlColor(color):
    color = color.lstrip("#")
    r1, r2, g1, g2, b1, b2 = color
    return int(b1 + b2, 16), int(g1 + g2, 16), int(r1 + r2, 16)


def getColorMapBW():
    return np.array([(i, i, i) for i in range(256)], dtype="B")


def getColorMapPastellGreen():
    return getColorMapFor("77dd77")


def getColorMapFor(onColor="ffffff", offColor="000000"):
    if isinstance(onColor, str):
        onColor = _htmlColor(onColor)
    if isinstance(offColor, str):
        offColor = _htmlColor(offColor)
    onR, onG, onB = onColor
    offR, offG, offB = offColor
    rDif, gDif, bDif = onR - offR, onG - offG, onB - offB
    rDif /= 255
    gDif /= 255
    bDif /= 255
    c = [(offR + rDif * i, offG + gDif * i, offB + bDif * i) for i in range(256)]
    return np.array(c, dtype="B")


def randomPastellColormap():
    return getColorMapFor(random.choice(COLORS_PASTELL))


def randomColormap(onColors=None, offColors=None, distinct=True):
    # Off
    if offColors is None:
        offColor = "ffffff"
    else:
        offColor = random.choice(offColors)

    # On
    if onColors is None:
        onColor = "000000"
    else:
        onColor = random.choice(onColors)
        i = 0
        while distinct and onColor == offColor and i < 100:
            onColor = random.choice(onColors)
            i += 1
        if distinct and onColor == offColor:
            raise ValueError("Cannot find valid on/off color combination")

    return getColorMapFor(onColor, offColor)


def visualizeColormap(colormap, height=10, width=256):
    cm = np.zeros((height, width, 3), dtype="B")
    for i in range(width):
        colorIndex = int(i / width * 255)
        c = colormap[colorIndex, 0:3]
        cm[:, i] = c
    return cm


class COLORMAPS:
    BW = getColorMapBW(),
    PastellGreen = getColorMapPastellGreen()


if __name__ == '__main__':
    for color in COLORS_DARK:
        img = colorblock(_htmlColor(color))
        cv2.imshow(color, img)
        cv2.waitKey(1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


class RandomColorProgressionIterator:
    def __init__(self, onColors=None, offColors=None):
        self.onColors = onColors
        self.offColors = offColors
        self.onIndex = 0
        self.offIndex = 0
        self.onColormap = []
        self.offColormap = []
        self.latestOnColor = random.choice(onColors)
        self.latestOffColor = random.choice(offColors)

        self.onDistinct = len(self.onColors) != 1
        self.offDistinct = len(self.offColors) != 1

    def __call__(self):
        self.onIndex += 1
        self.offIndex += 1
        if self.onIndex >= len(self.onColormap):
            self.onIndex = 0
            self.onColormap = randomColormap(onColors=self.onColors, offColors=[self.latestOnColor],
                                             distinct=self.onDistinct)
            self.latestOnColor = self.onColormap[255]

        if self.offIndex >= len(self.offColormap):
            self.offIndex = 0
            self.offColormap = randomColormap(onColors=self.offColors, offColors=[self.latestOffColor],
                                              distinct=self.offDistinct)
            self.latestOffColor = self.offColormap[255]

        return getColorMapFor(self.onColormap[self.onIndex], self.offColormap[self.offIndex])

    def invert(self):
        self.onColors, self.offColors = self.offColors, self.onColors
        self.onColormap, self.offColormap = self.offColormap, self.onColormap
        self.latestOnColor, self.latestOffColor = self.latestOffColor, self.latestOnColor
        self.onIndex, self.offIndex = self.offIndex, self.onIndex
