import os
import unittest
from shutil import rmtree

from utils import boardIO
from gol import GoL

TEST_DIR = "data/tests/"


class BoardIOTest(unittest.TestCase):
    def testNormalCharset(self):
        self.assertNotEqual(boardIO.CHAR_ON, boardIO.CHAR_OFF)
        self.assertNotEqual(boardIO.CHAR_ON, boardIO.CHAR_DELIMITER)
        self.assertNotEqual(boardIO.CHAR_OFF, boardIO.CHAR_DELIMITER)

    def testSaveBoardNormal(self):
        dir_ = TEST_DIR + "dir/"
        filename = dir_ + "saveBoard.board"
        rmtree(dir_, ignore_errors=True)
        board = [[0 for _ in range(10)] for _ in range(10)]
        boardIO.saveBoard(board, filename)
        self.assertTrue(os.path.exists(filename))

    def testNormalRandomSmall(self):
        filename = TEST_DIR + "small.board"

        originalBoard = GoL.createRandomBoard(121, 106)
        boardIO.saveBoard(originalBoard, filename)
        loadedBoard = boardIO.loadBoard(filename)
        self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))

    def testNormalRandomMedium(self):
        filename = TEST_DIR + "medium.board"

        originalBoard = GoL.createRandomBoard(1500, 1751)
        boardIO.saveBoard(originalBoard, filename)
        loadedBoard = boardIO.loadBoard(filename)
        self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))

    def testSaveBoardCompressed(self):
        dir_ = TEST_DIR + "dir/"
        filename = dir_ + "saveBoard.boardC"
        rmtree(dir_, ignore_errors=True)
        board = [[0 for _ in range(10)] for _ in range(10)]
        boardIO.saveCompressedBoard(board, filename)
        self.assertTrue(os.path.exists(filename))

    def testCompressedRandomSmall(self):
        filename = TEST_DIR + "small.boardC"

        originalBoard = GoL.createRandomBoard(121, 106)
        boardIO.saveCompressedBoard(originalBoard, filename)
        loadedBoard = boardIO.loadCompressedBoard(filename)
        self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))

    def testCompressedRandomMedium(self):
        filename = TEST_DIR + "medium.boardC"

        originalBoard = GoL.createRandomBoard(1500, 1751)
        boardIO.saveCompressedBoard(originalBoard, filename)
        loadedBoard = boardIO.loadCompressedBoard(filename)
        self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))


class GoLRulesTest(unittest.TestCase):
    def testSmallBoard(self):
        board = [
            [1, 1, 0, 1, 0],
            [1, 0, 1, 0, 1],
            [0, 0, 1, 0, 1],
            [1, 1, 0, 1, 0],
            [1, 0, 0, 0, 0],
        ]

        nextBoardValidated = [
            [1, 1, 1, 1, 0],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 1, 1, 1, 0],
            [1, 1, 0, 0, 0]
        ]
        gol = GoL(initBoard=board)
        gol.step()
        nextBoard = gol.board
        self.assertTrue(boardIO.checkEquals(nextBoard, nextBoardValidated))

    def testMediumBoard(self):
            board = boardIO.loadCompressedBoard(TEST_DIR + "mediumRulesTest")
            validBoard1 = boardIO.loadCompressedBoard(TEST_DIR + "mediumRulesTestResult1")
            validBoard21 = boardIO.loadCompressedBoard(TEST_DIR + "mediumRulesTestResult21")

            gol = GoL(initBoard=board)
            gol.step()
            nextBoard = gol.board
            self.assertTrue(boardIO.checkEquals(nextBoard, validBoard1))
            gol.step(20)
            nextBoard = gol.board
            self.assertTrue(boardIO.checkEquals(nextBoard, validBoard21))

    def test2Oszillator1(self):
        board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        gol = GoL(initBoard=board)
        gol.step(2)
        nextBoard = gol.board

        self.assertTrue(boardIO.checkEquals(nextBoard, board))

    def test2Oszillator2(self):
        board = [
            [1, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ]

        gol = GoL(initBoard=board)
        gol.step(2)
        nextBoard = gol.board

        self.assertTrue(boardIO.checkEquals(nextBoard, board))

    def test5Oszillator(self):
        board = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        gol = GoL(initBoard=board)
        gol.step(5)
        nextBoard = gol.board

        self.assertTrue(boardIO.checkEquals(nextBoard, board))

    def testStatic(self):
        board = [
            [1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        gol = GoL(initBoard=board)
        gol.step(100)
        nextBoard = gol.board

        self.assertTrue(boardIO.checkEquals(nextBoard, board))


if __name__ == '__main__':
    unittest.main()
