import os
import random
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

import utils.colormaps as cm
from gol import GoL
from imageRenderer import RenderSettings, renderImage
from utils import boardIO


class GoLVideoRenderer:
    def __init__(self, filename, videoWidth, videoHeight, fps=30, fpg=1, showNeighbourCount=False, showGridlines=False,
                 colormap=None, renderer=None):
        self.filename = filename
        self.videoWidth = int(videoWidth)
        self.videoHeight = int(videoHeight)

        # Rendersettings
        self.renderer = renderer if renderer is not None else renderImage
        self.renderSettings = RenderSettings(self.videoWidth, self.videoHeight)
        self.renderSettings.colormap = colormap
        self.renderSettings.showNeighbours = showNeighbourCount
        self.renderSettings.showGridlines = showGridlines
        self.renderSettings.onColorIndex = 255
        self.renderSettings.offColorIndex = 0

        # Videosettings
        self.fps = fps
        self.fpg = fpg
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        os.makedirs(Path(filename).parent, exist_ok=True)
        self.vidOut = cv2.VideoWriter(self.filename, fourcc, self.fps, (self.videoWidth, self.videoHeight), isColor=1)
        self.frameNo = 0
        self.oldImage = None

    def appendGoL(self, gol: GoL, maxGenerations=100,
                  tl=(0, 0), br=(-1, -1), preview=False, abortCondition=None, onColorChange=0, offColorChange=0,
                  **kwargs):

        minTL, maxTL = tl
        minBR, maxBR = br
        try:
            _, _ = minTL
        except TypeError:
            minTL = maxTL = tl

        try:
            _, _ = minBR
        except TypeError:
            minBR = maxBR = br

        progressRange = tqdm(range(maxGenerations + 1))
        for i in progressRange:
            for frameNo in range(self.fpg):
                curTL = [min_tl + (max_tl - min_tl) / (maxGenerations * self.fpg) * ((i - 1) * self.fpg + frameNo) for
                         min_tl, max_tl in zip(minTL, maxTL)]
                curBR = [min_br + (max_br - min_br) / (maxGenerations * self.fpg) * ((i - 1) * self.fpg + frameNo) for
                         min_br, max_br in zip(minBR, maxBR)]
                self.renderSettings.topLeft = curTL
                self.renderSettings.bottomRight = curBR

                img = self.renderer(gol, self.renderSettings)
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
            self.renderSettings.onColorIndex = min(max(self.renderSettings.onColorIndex + changeOnColor, 128), 255)
            self.renderSettings.offColorIndex = min(max(self.renderSettings.offColorIndex + changeOffColor, 0), 128)

    def __del__(self):
        self.finish()

    def finish(self):
        self.vidOut.release()

    def addHighlight(self, position, color):
        if isinstance(color, str):
            color = cm._htmlColor(color)
        self.renderSettings.highlights.append((position, color))

    def addText(self, position, text, color):
        if isinstance(color, str):
            color = cm._htmlColor(color)
        self.renderSettings.texts.append((position, text, color))

    def renderImage(self, gol: GoL):
        if not isinstance(gol, GoL):
            gol = GoL(gol)
        return self.renderer(gol, self.renderSettings)


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

    # c = cm.randomColormap(onColors=cm.COLORS_PASTELL, offColors=cm.COLORS_DARK)
    # c = cm.randomColormap()

    goalFrames = 10 * 60 * vid.fps
    k = 2
    while vid.frameNo < goalFrames:
        vid.colormap = cm.RandomColorProgressionIterator(cm.COLORS_DARK, ["ffffff"])
        print(f"Current Frames: {vid.frameNo}. Goal: {goalFrames}")
        rndThresh = random.random() * 0.2 + 0.4  # range 0.4 - 0.6
        print(f"On Cells: ~{rndThresh * 100:.2f}%")
        board = boardIO.createRandomBoard(192 * k, 108 * k, rndThreshold=rndThresh)
        gol = GoL(board)
        abort = AbortDifHandler(board, extendGenerations=150)
        vid.appendGoL(gol, 1000, abortCondition=AbortDifHandler(board), onColorChange=0, offColorChange=0)
        try:
            vid.colormap.invert()
        except AttributeError:
            pass
        # vid.colormap = cm.randomColormap(onColors=cm.COLORS_DARK, offColors=["ffffff"])
