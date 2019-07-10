import itertools
import random

from gol import GoL
from golImage import GoLImageRenderer
from utils import boardIO

if __name__ == '__main__':
    import utils.colormaps as cm

    golTraining = GoLImageRenderer("../data/images/training", 512, 512, colormap=cm.COLORMAP_WHITE_GREEN, showGridlines=True)
    for i in range(20):
        # Base settings
        rndThresh = random.random() * 0.4 + 0.2  # range 0.2 - 0.6
        board = boardIO.createRandomBoard(10, 10, rndThresh)
        gol = GoL(board)

        # Marked tiles
        colors = cm.COLORS_MARK3
        n = len(colors)

        allTiles = itertools.product(range(1, gol.width - 1), range(1, gol.height - 1))
        nTiles = random.sample(list(allTiles), n)
        for color, tile in zip(colors, nTiles):
            golTraining.addHighlight(tile, color, 5)

        # Record images
        golTraining.renderSettings.showNeighbours = False
        gol.name = f"Training{i:02d}_"
        golTraining.appendGoL(gol)

        gol.reset()
        gol.name = f"Training{i:02d}N_"
        golTraining.renderSettings.showNeighbours = True
        golTraining.appendGoL(gol)
