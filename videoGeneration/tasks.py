import utils.colormaps as cm
from gol import GoL
from golImage import GoLImageRenderer
from utils import boardIO

if __name__ == '__main__':
    colormap = cm.COLORMAP_WHITE_GREEN
    golVideo = GoLImageRenderer("../data/images/tasks2", 540, 540, colormap=colormap)

    # Block
    board = boardIO.emptyBoard(3, 3)
    board[0][1] = 1
    board[0][2] = 1
    board[1][1] = 1
    board[1][2] = 1
    gol = GoL(board)
    gol.name = "block"
    golVideo.appendGoL(gol, maxGenerations=0)

    # o
    board = boardIO.emptyBoard(3, 3)
    board[1][0] = 1  # Top
    board[2][1] = 1  # Right
    board[1][2] = 1  # Bottom
    board[0][1] = 1  # Left
    gol = GoL(board)
    gol.name = "o"
    golVideo.appendGoL(gol, maxGenerations=0)

    # Blinker
    board = boardIO.emptyBoard(3, 3)
    board[1][0] = 1
    board[1][1] = 1
    board[1][2] = 1
    gol = GoL(board)
    gol.name = "blinker"
    golVideo.appendGoL(gol, maxGenerations=1)

    # Glider
    board = boardIO.emptyBoard(3, 3)
    board[0][0] = 1
    board[1][0] = 1
    board[1][2] = 1
    board[2][0] = 1
    board[2][1] = 1
    gol = GoL(board)
    gol.name = "glider"
    golVideo.appendGoL(gol, maxGenerations=0)
