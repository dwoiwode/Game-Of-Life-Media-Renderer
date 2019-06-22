import os
import unittest
from shutil import rmtree

import boardIO
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


if __name__ == '__main__':
    unittest.main()
