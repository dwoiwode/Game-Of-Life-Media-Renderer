import random

import utils.colormaps as cm
from VideoRenderer import AbortDifHandler, GoLVideoRenderer
from gol import GoL
from utils import boardIO

if __name__ == '__main__':
    vid = GoLVideoRenderer("../data/videos/colorChangingNewColorOnChange2.avi", 1920, 1080, fps=24,
                           colormap=cm.getColorMapFor("298A08", "ffffff"))

    goalFrames = 10 * 60 * vid.fps
    k = 2  # Resolution * k = Number of cells
    while vid.frameNo < goalFrames:
        vid.renderSettings.colormap = cm.RandomColorProgressionIterator(cm.COLORS_DARK, ["ffffff"])
        print(f"Current Frames: {vid.frameNo}. Goal: {goalFrames}")
        rndThresh = random.random() * 0.2 + 0.4  # range 0.4 - 0.6
        print(f"On Cells: ~{rndThresh * 100:.2f}%")
        board = boardIO.createRandomBoard(192 * k, 108 * k, rndThreshold=rndThresh)
        gol = GoL(board)
        abort = AbortDifHandler(board, extendGenerations=150)
        vid.appendGoL(gol, 1000, abortCondition=AbortDifHandler(board), onColorChange=0, offColorChange=0)
        # try:
        #     vid.colormap.invert()
        # except AttributeError:
        #     pass
        # vid.colormap = cm.randomColormap(onColors=cm.COLORS_DARK, offColors=["ffffff"])
