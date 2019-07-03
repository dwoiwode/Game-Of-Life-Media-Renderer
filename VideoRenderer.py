import os
import random
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

import utils.colormaps as cm
from gol import GoL
from utils import boardIO


class GoLVideoRenderer:
    def __init__(self, filename, videoWidth, videoHeight, fps=30, showNeighbourCount=False, showGridlines=False,
                 colormap=None):
        self.filename = filename
        self.canvasWidth = int(videoWidth)
        self.canvasHeight = int(videoHeight)
        self.showNeighbours = showNeighbourCount
        self.showGridlines = showGridlines
        self.colormap = colormap
        self.fps = fps

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        os.makedirs(Path(filename).parent, exist_ok=True)
        self.vidOut = cv2.VideoWriter(self.filename, fourcc, self.fps, (self.canvasWidth, self.canvasHeight), isColor=1)
        self.frameNo = 0
        self.oldImage = None

        self.onColorIndex = 255
        self.offColorIndex = 0

        self.hightlights = []
        self.texts = []

    def appendGoL(self, gol: GoL, maxGenerations=100,
                  tl=(0, 0), br=(-1, -1), preview=False, abortCondition=None, onColorChange=0, offColorChange=0,
                  **kwargs):
        progressRange = tqdm(range(maxGenerations))
        for i in progressRange:
            img = self.renderImage(gol, tl=tl, br=br)
            if preview:
                cv2.imshow(self.filename, img)
                cv2.setWindowTitle(self.filename, f"{self.filename} - Frame {self.frameNo}")
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.finish()
                    break

            self.vidOut.write(img)

            self.frameNo += 1

            gol.step()

            if abortCondition is not None and abortCondition(gol):
                progressRange.close()
                return

            changeOnColor = (0.5 - random.random()) * 2 * onColorChange
            changeOffColor = (0.5 - random.random()) * 2 * offColorChange
            self.onColorIndex = min(max(self.onColorIndex + changeOnColor, 128), 255)
            self.offColorIndex = min(max(self.offColorIndex + changeOffColor, 0), 128)

    def __del__(self):
        self.finish()

    def finish(self):
        self.vidOut.release()

    def renderImage(self, gol: GoL, tl=(0, 0), br=(-1, -1)):
        img = np.zeros((self.canvasHeight, self.canvasWidth), dtype="B")

        xMin, yMin = tl
        xMax, yMax = br
        if xMax < 0:
            xMax += gol.width
        if yMax < 0:
            yMax += gol.height

        scaling = min(self.canvasWidth / (xMax - xMin + 1), self.canvasHeight / (yMax - yMin + 1))
        lastX = 0

        font = cv2.FONT_HERSHEY_PLAIN
        textScaling = 0.05
        if self.showNeighbours:
            while max(cv2.getTextSize("0", font, textScaling, 1)[0]) < scaling * 0.9:
                textScaling += 0.05

        for x in range(xMin, xMax + 1):
            nextX = int((x + 1 - xMin) * scaling)
            lastY = 0
            for y in range(yMin, yMax + 1):
                nextY = int((y + 1 - yMin) * scaling)

                grayValue = self.onColorIndex if gol.getXY(x, y) else self.offColorIndex
                if self.showGridlines:
                    cv2.rectangle(img, (lastX, lastY), (nextX, nextY), 255, 2)

                cv2.rectangle(img, (lastX, lastY), (nextX, nextY), grayValue, -1)
                lastY = nextY

                if self.showNeighbours:
                    nb = gol.countNeighbours(x, y)
                    if nb == 0:
                        continue
                    textColor = [255 - grayValue for _ in range(3)]
                    actualNeighbours = nb - gol.getXY(x, y)
                    cv2.putText(img, str(actualNeighbours), (int(lastX + 0.05 * scaling), int(lastY - 0.05 * scaling)),
                                font, textScaling, textColor, 1,
                                cv2.LINE_AA)
            lastX = nextX

        coloredImg = cm.colorize(img, self.colormap)
        for position, text, color in self.texts:
            tmp1, tmp2 = position
            x = int((tmp1 - xMin + 0.05) * scaling)
            y = int((tmp2 - yMin + 0.95) * scaling)
            cv2.putText(coloredImg, text, (x, y),
                        font, textScaling, color, 1,
                        cv2.LINE_AA)

        for position, color in self.hightlights:
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
            cv2.rectangle(coloredImg, (x1, y1), (x2, y2), color, 4)
        return coloredImg

    def addHighlight(self, position, color):
        if isinstance(color, str):
            color = cm._htmlColor(color)
        self.hightlights.append((position, color))

    def addText(self, position, text, color):
        if isinstance(color, str):
            color = cm._htmlColor(color)
        self.texts.append((position, text, color))


class AbortDifHandler:
    def __init__(self, initBoard, extendGenerations=1):
        self.oldBoard = initBoard
        self.oldDif = np.zeros_like(initBoard)
        self.nGen = 0
        self.extendGenerations = extendGenerations

    def __call__(self, gol: GoL, **kwargs):
        dif = np.abs(np.subtract(self.oldBoard, gol.board))
        dif2 = np.abs(np.subtract(dif, self.oldDif))
        self.oldDif = dif
        self.oldBoard = gol.board.astype(int)

        difSum = np.sum(dif)
        difSum2 = np.sum(dif2)

        if difSum2 == 0:
            return True
        if difSum > difSum2:
            self.nGen += 1
            if self.nGen > self.extendGenerations:
                return True
        else:
            self.nGen = 0
        return False


if __name__ == '__main__':
    vid = GoLVideoRenderer("data/videos/colorChangingLong3.avi", 1920, 1080, fps=24,
                           colormap=cm.getColorMapFor("298A08", "ffffff"))

    vid.colormap = cm.RandomColorProgressionIterator(cm.COLORS_DARK, ["ffffff"])

    c = cm.randomColormap(onColors=cm.COLORS_PASTELL, offColors=cm.COLORS_DARK)
    # c = cm.randomColormap()

    goalFrames = 10 * 60 * vid.fps
    while vid.frameNo < goalFrames:
        print(f"Current Frames: {vid.frameNo}. Goal: {goalFrames}")
        rndThresh = random.random() * 0.2 + 0.4  # range 0.4 - 0.6
        print(f"On Cells: ~{rndThresh * 100:.2f}%")
        k = 3
        board = boardIO.createRandomBoard(192 * k, 108 * k, rndThreshold=rndThresh)
        gol = GoL(board)
        abort = AbortDifHandler(board, extendGenerations=150)
        vid.appendGoL(gol, 1000, abortCondition=AbortDifHandler(board), onColorChange=0, offColorChange=0)
        try:
            vid.colormap.invert()
        except AttributeError:
            pass
        # vid.colormap = cm.randomColormap(onColors=cm.COLORS_DARK, offColors=["ffffff"])
