import time

import numpy as np

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
    def __init__(self, initBoard, countEdge=False):
        self.width, self.height = len(initBoard), len(initBoard[0])

        self.generation = 0

        self.oldBoard = self.newBoard(0)
        self.board = np.asarray(initBoard)
        self._initialBoard = self.board
        self.countEdge = countEdge
        if initBoard is None:
            self.initRandom()

        self.livingCells = property(self._countLivingCells)

    def reset(self):
        self.board = self._initialBoard

    def getXY(self, x, y):
        return self.board[x, y]

    def setXY(self, x, y, value):
        self.board[x, y] = value

    def _countLivingCells(self):
        return np.sum(self.board)

    @timeit
    def step(self, n=1):
        for i in range(n):
            self._singlestep()

    @timeit
    def _singlestep(self):
        G = self.board.astype(int)
        N = np.zeros_like(G)
        G = np.pad(G, pad_width=1, mode='constant', constant_values=0)
        N[:, :] = (G[:-2, :-2] + G[:-2, 1:-1] + G[:-2, 2:] +
                   G[1:-1, :-2] + G[1:-1, 2:] +
                   G[2:, :-2] + G[2:, 1:-1] + G[2:, 2:])

        self.board = np.logical_or(N == 3, np.logical_and(G[1:-1, 1:-1] == 1, N == 2))

        self.generation += 1

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
                    sum_ += self.getXY(thisX, thisY)
                except IndexError:
                    sum_ += self.countEdge
        return sum_

    def newBoard(self, initValue: int = 0):
        return np.full((self.width, self.height), initValue)

    def initRandom(self):
        self.board = GoL.createRandomBoard(self.width, self.height)

    @classmethod
    def createRandomBoard(cls, width, height, rndThreshold=0.5):
        board = np.zeros((width, height))
        rnd = np.random.random((width, height))
        board[np.where(rnd < rndThreshold)] = 1
        return board
