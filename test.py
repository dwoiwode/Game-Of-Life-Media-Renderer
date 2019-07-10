import os
import unittest
from shutil import rmtree

from utils import boardIO
from gol import GoL

TEST_DIR = "data/tests/"


class BoardIOTest(unittest.TestCase):
    SMALL_SIZE = (121, 106)
    MEDIUM_SIZE = (1500, 1751)
    BIG_SIZE = (5829, 2962)

    def testNormalCharset(self):
        self.assertNotEqual(boardIO.CHAR_ON, boardIO.CHAR_OFF)
        self.assertNotEqual(boardIO.CHAR_ON, boardIO.CHAR_DELIMITER)
        self.assertNotEqual(boardIO.CHAR_OFF, boardIO.CHAR_DELIMITER)

    def testLoadFileNotFound(self):
        filename = TEST_DIR + "filenotfound"
        self.assertRaises(FileNotFoundError, lambda: boardIO.loadBoard(filename))
        self.assertRaises(FileNotFoundError, lambda: boardIO.loadCompressedBoard(filename))

    def testInvalidChar(self):
        filecontent = "_X\n1"
        filename = TEST_DIR + "invalidChar.board"
        with open(filename, "w") as d:
            d.write(filecontent)

        self.assertRaises(ValueError, lambda: boardIO.loadBoard(filename))


    def testSaveBoardNormal(self):
        dir_ = TEST_DIR + "dir/"
        filename = dir_ + "saveBoard.board"
        rmtree(dir_, ignore_errors=True)
        board = [[0 for _ in range(10)] for _ in range(10)]
        boardIO.saveBoard(board, filename)
        self.assertTrue(os.path.exists(filename))

    def testNormalRandomSmall(self):
        filename = TEST_DIR + "small.board"

        originalBoard = boardIO.createRandomBoard(*BoardIOTest.SMALL_SIZE)
        boardIO.saveBoard(originalBoard, filename)
        loadedBoard = boardIO.loadBoard(filename)
        self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))

    def testNormalRandomMedium(self):
        filename = TEST_DIR + "medium"

        originalBoard = boardIO.createRandomBoard(*BoardIOTest.MEDIUM_SIZE)
        boardIO.saveBoard(originalBoard, filename)
        loadedBoard = boardIO.loadBoard(filename)
        self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))

    # def testNormalRandomBig(self):
    #     filename = TEST_DIR + "big.board"
    #
    #     originalBoard = boardIO.createRandomBoard(*BoardIOTest.BIG_SIZE)
    #     boardIO.saveBoard(originalBoard, filename)
    #     loadedBoard = boardIO.loadBoard(filename)
    #     self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))

    def testSaveBoardCompressed(self):
        dir_ = TEST_DIR + "dir/"
        filename = dir_ + "saveBoard.boardC"
        rmtree(dir_, ignore_errors=True)
        board = [[0 for _ in range(10)] for _ in range(10)]
        boardIO.saveCompressedBoard(board, filename)
        self.assertTrue(os.path.exists(filename))

    def testCompressedRandomSmall(self):
        filename = TEST_DIR + "small.boardC"

        originalBoard = boardIO.createRandomBoard(*BoardIOTest.SMALL_SIZE)
        boardIO.saveCompressedBoard(originalBoard, filename)
        loadedBoard = boardIO.loadCompressedBoard(filename)
        self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))

    def testCompressedRandomMedium(self):
        filename = TEST_DIR + "medium"

        originalBoard = boardIO.createRandomBoard(*BoardIOTest.MEDIUM_SIZE)
        boardIO.saveCompressedBoard(originalBoard, filename)
        loadedBoard = boardIO.loadCompressedBoard(filename)
        self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))

    # def testCompressedRandomBig(self):
    #     filename = TEST_DIR + "big.boardC"
    #
    #     originalBoard = boardIO.createRandomBoard(*BoardIOTest.BIG_SIZE)
    #     boardIO.saveCompressedBoard(originalBoard, filename)
    #     loadedBoard = boardIO.loadCompressedBoard(filename)
    #     self.assertTrue(boardIO.checkEquals(originalBoard, loadedBoard))

    def testEmptyBoard(self):
        board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        boardTest = boardIO.emptyBoard(len(board), len(board[0]))
        self.assertTrue(boardIO.checkEquals(board, boardTest))


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
