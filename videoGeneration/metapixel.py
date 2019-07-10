import cv2

import utils.colormaps as cm
from VideoRenderer import GoLVideoRenderer
from imageRenderer import fastImage
from utils import boardIO

if __name__ == '__main__':
    board = boardIO.loadRLE("../data/boards/metapixel-on-off-1.rle")
    # board = boardIO.loadRLE("../data/boards/Turing-Machine-3-state.rle")
    # golVideo = GoLVideo(board,len(board), len(board[0]))
    # golVideo.recordImages("../data/images/metapixel",0,colormap=cm.COLORMAP_BLACK_WHITE)
    # board = boardIO.createRandomBoard(20,1916)
    # board = boardIO.addBorder(board, 100)
    n = 78_018

    golVideo = GoLVideoRenderer("../data/videos/metapixel-on-off.avi", len(board), len(board[0]), fps=120,
                                colormap=cm.COLORMAP_BLACK_WHITE,
                                renderer=fastImage)

    img = golVideo.renderImage(board)
    cv2.imwrite("metapixel-1.jpg", img)
    # golVideo.renderSettings.topLeft= (90,90)
    # golVideo.renderSettings.bottomRight = (-91,-91)
    # cv2.namedWindow("metapixel",cv2.WINDOW_NORMAL)
    # cv2.imshow("metapixel", golVideo.renderImage(board))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # golVideo.name = "metapixel"
    # # fastImage(board, "test.jpg")
    # img = golVideo.appendGoL(GoL(board), maxGenerations=n, tl=(90, 90), br=(-91, -91), preview=True)
