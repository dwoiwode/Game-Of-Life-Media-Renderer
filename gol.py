import random
import time

DEPTH = 0
ENABLE_TIMEIT = False


def timeit(func):
    def wrapped(*args, **kwargs):
        global DEPTH
        t1 = time.time()
        DEPTH += 1
        ret = func(*args, **kwargs)
        DEPTH -= 1
        t2 = time.time()
        if ENABLE_TIMEIT:
            print(f"[{t2:.20f}]{DEPTH * '  '}[{func.__name__}] Took {t2 - t1} seconds")
        return ret

    return wrapped


class GoL:
    def __init__(self, initBoard=None, countEdge=False):
        self.width, self.height = len(initBoard), len(initBoard[0])

        self.generation = 0

        self.oldBoard = self.newBoard(0)
        self.board = initBoard
        self.countEdge = countEdge
        if initBoard is None:
            self.initRandom()

    def getXY(self, x, y):
        return self.board[x][y]

    def setXY(self, x, y, value):
        self.board[x][y] = value

    @timeit
    def step(self, n=1):
        for i in range(n):
            self._singlestep()

    @timeit
    def _singlestep(self):
        def getValue(x, y):
            neighbours = self.countNeighbours(x, y)
            if neighbours == 3:
                return 1
            elif neighbours == 4:
                return self.getXY(x, y)
            else:
                return 0

        self.latestManualTile = None
        board = self.newBoard()
        for x in range(self.width):
            for y in range(self.height):
                board[x][y] = getValue(x, y)
                self.oldBoard[x][y] = max(self.oldBoard[x][y] / 3 * 2, board[x][y])

        self.generation += 1
        self.board = board

    def clearBoard(self):
        self.board = self.newBoard()

    def countNeighbours(self, x, y):
        sum_ = 0
        for i in range(3):
            for ii in range(3):
                thisX = x + i - 1
                thisY = y + ii - 1
                if thisX < 0 or thisY < 0:
                    sum_ += self.countEdge
                    continue
                try:
                    sum_ += self.board[thisX][thisY]
                except IndexError:
                    sum_ += self.countEdge
        return sum_

    def newBoard(self, initValue: callable or int = 0):
        if initValue in (0, 1):
            return [[round(initValue) for _ in range(self.height)] for _ in range(self.width)]
        return [[round(initValue()) for _ in range(self.height)] for _ in range(self.width)]

    def initRandom(self):
        self.board = GoL.createRandomBoard(self.width, self.height)

    @classmethod
    def createRandomBoard(cls, width, height):
        return [[round(random.random()) for _ in range(height)] for _ in range(width)]
