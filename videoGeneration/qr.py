import utils.colormaps as cm
from VideoRenderer import GoLVideoRenderer
from gol import GoL
from utils import boardIO

if __name__ == '__main__':
    board = boardIO.fromImageToSpecificSize("../data/imgs/qr-github.comdwoiwodeGame-Of-Life-Media-Renderer.png",
                                            size=(33, 33))
    border = 500
    board = boardIO.addBorder(board, border)
    golVideo = GoLVideoRenderer("../data/videos/qr_github2.avi", 1080, 1080, fps=60, fpg=2,
                                colormap=cm.COLORMAP_WHITE_GREEN)
    tl = (border, border)
    br = (-border - 1, -border - 1)
    gol = GoL(board)
    golVideo.addHighlight((tl, (border + 33, border + 33)), "ff0000")
    golVideo.appendGoL(gol, 120, tl=tl, br=br, preview=True)

    tl = (tl, (450, 450))
    br = (br, (-451, -451))
    golVideo.appendGoL(gol, 80, tl=tl, br=br, preview=True)
    golVideo.appendGoL(gol, 500, tl=tl[1], br=br[1], preview=True)
    # gol = GoLPygame(initBoard=board, colormap=cm.COLORMAP_WHITE_BLACK)
    # gol.start()
