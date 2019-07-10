import os
import random
from pathlib import Path

import cv2
from tqdm import tqdm

import utils.colormaps as cm
from gol import GoL
from imageRenderer import RenderSettings, renderImage


class GoLImageRenderer:
    def __init__(self, folder, width, height, fpg=1, showNeighbourCount=False, showGridlines=False,
                 colormap=None, renderer=None):
        self.folder = folder

        # Rendersettings
        self.renderer = renderer if renderer is not None else renderImage
        self.renderSettings = RenderSettings(width, height)
        self.renderSettings.colormap = colormap
        self.renderSettings.showNeighbours = showNeighbourCount
        self.renderSettings.showGridlines = showGridlines
        self.renderSettings.onColorIndex = 255
        self.renderSettings.offColorIndex = 0

        # Videosettings
        self.fpg = fpg
        os.makedirs(Path(folder), exist_ok=True)
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

        maxGenerations += 1
        progressRange = tqdm(range(maxGenerations))
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
                    cv2.imshow(self.folder, img)
                    cv2.setWindowTitle(self.folder, f"{self.folder} - {i} ({frameNo}/{self.fpg})")
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                cv2.imwrite(str(Path(self.folder)) + f"/{gol.name}_{gol.generation}_{frameNo:02d}.jpg", img)
            gol.step()

            if abortCondition is not None and abortCondition(gol):
                progressRange.close()
                return

            changeOnColor = (0.5 - random.random()) * 2 * onColorChange
            changeOffColor = (0.5 - random.random()) * 2 * offColorChange
            self.renderSettings.onColorIndex = min(max(self.renderSettings.onColorIndex + changeOnColor, 128), 255)
            self.renderSettings.offColorIndex = min(max(self.renderSettings.offColorIndex + changeOffColor, 0), 128)

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
