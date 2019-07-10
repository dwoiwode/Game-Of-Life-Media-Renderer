import utils.colormaps as  cm
from VideoRenderer import GoLVideoRenderer
from gol import GoL
from golImage import GoLImageRenderer
from imageRenderer import renderImage
from utils import boardIO

if __name__ == '__main__':
    board = boardIO.loadBoard("../data/boards/r-pentomino")
    board = boardIO.addBorder(board, 400)
    colormap = cm.COLORMAP_WHITE_GREEN

    tl = (350, 350)
    br = (-351, -351)
    # === Static Images ===
    golImages = GoLImageRenderer("../data/images/r-pentomino", 1080, 1080, colormap=colormap)
    gol = GoL(board)
    gol.name = "r-pentomino"
    golImages.appendGoL(gol, maxGenerations=1199, tl=tl, br=br)

    # === Zoom out Video ===
    gol = GoL(board)
    golVideo = GoLVideoRenderer("../data/videos/r-pentomino-zoom.avi", 1080, 1080, fps=24, fpg=4, colormap=colormap,
                                renderer=renderImage)
    tl = ((398, 398), tl)
    br = ((-399, -399), br)
    # golVideo.appendGoL(gol, 200, tl, br,preview=False)
    golVideo.fpg = 1
    golVideo.appendGoL(gol, 792, tl, br, preview=False)
