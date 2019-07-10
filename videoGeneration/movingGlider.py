import utils.colormaps as cm
from VideoRenderer import GoLVideoRenderer
from gol import GoL
from utils import boardIO

if __name__ == '__main__':
    gliderBoard = boardIO.emptyBoard(15, 15)
    gliderBoard[5][7] = True
    gliderBoard[6][7] = True
    gliderBoard[6][9] = True
    gliderBoard[7][7] = True
    gliderBoard[7][8] = True

    golVid = GoLVideoRenderer("../data/videos/movingGlider2.avi", 1080 / 2, 1080 / 2, fps=24, showGridlines=True,
                              colormap=cm.COLORMAP_WHITE_GREEN, fpg=12)

    tl = [
        (2, 3),
        (3, 2),
    ]
    br = [
        (-4, -3),
        (-3, -4),
    ]
    golVid.appendGoL(GoL(gliderBoard), 4, preview=True, tl=tl, br=br)
    tl = [
        (2, 3),
        (3, 2),
    ]
    br = [
        (-4, -3),
        (-3, -4),
    ]
    golVid.appendGoL(GoL(gliderBoard), 4, preview=True, tl=tl, br=br)
    tl = [
        (2, 3),
        (3, 2),
    ]
    br = [
        (-4, -3),
        (-3, -4),
    ]
    golVid.appendGoL(GoL(gliderBoard), 4, preview=True, tl=tl, br=br)
    tl = [
        (2, 3),
        (3, 2),
    ]
    br = [
        (-4, -3),
        (-3, -4),
    ]
    golVid.appendGoL(GoL(gliderBoard), 4, preview=True, tl=tl, br=br)
    tl = [
        (2, 3),
        (3, 2),
    ]
    br = [
        (-4, -3),
        (-3, -4),
    ]
    golVid.appendGoL(GoL(gliderBoard), 4, preview=True, tl=tl, br=br)

    golVid.finish()
