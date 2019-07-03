import os
from pathlib import Path

import cv2
import numpy as np

# Default chars used when saving boards
CHAR_ON = "X"
CHAR_OFF = "_"
CHAR_DELIMITER = "\n"

# Characters reserved for length.
# 1 => Maxsize = 256^1 - 1 = 255 is maxWidth/maxHeight
# 2 => Maxsize = 256^3 - 1 = 65_535 is maxWidth/maxHeight
# 3 => Maxsize = 256^3 - 1 = 16_777_215 is maxWidth/maxHeight
COMPRESSED_DIM_LEN = 3


# ===== from File =====
# === Normal ===
def saveBoard(board, filename, on=CHAR_ON, off=CHAR_OFF, delimiter=CHAR_DELIMITER):
    s = delimiter.join(
        "".join(
            on if board[x][y] else off
            for x in range(len(board))
        )
        for y in range(len(board[0]))
    )
    os.makedirs(Path(filename).parent, exist_ok=True)
    with open(filename, "w") as d:
        d.write(off + on + delimiter)
        d.write(s)


def loadBoard(filename):
    if not os.path.exists(filename):
        if os.path.exists(filename + ".board"):
            filename += ".board"
        else:
            raise FileNotFoundError
    with open(filename, "r") as d:
        off, on, delimiter = d.read(3)
        data = [[c for c in row] for row in d.read().split(delimiter) if row.strip()]

    board = [[0 for _ in range(len(data))] for _ in range(len(data[0]))]
    for x in range(len(board)):
        for y in range(len(board[0])):
            if data[y][x] == on:
                board[x][y] = 1
            elif data[y][x] == off:
                board[x][y] = 0
            else:
                print(f"Invalid char at ({x},{y}): {data[x][y]}")
    return board


# === Compressed ===
# Compression shrinks size to ~12%, but increases load time for big files
def saveCompressedBoard(board, filename):
    singleBinString = "".join("".join("1"
                                      if board[x][y]
                                      else "0"
                                      for x in range(len(board)))
                              for y in range(len(board[0])))

    singleBinString += (8 - len(singleBinString) % 8) * "0"
    s = ""
    for i in range(len(singleBinString) // 8):
        s += chr(int(singleBinString[i * 8:(i + 1) * 8], 2))

    os.makedirs(Path(filename).parent, exist_ok=True)
    with open(filename, "wb") as d:
        w = len(board).to_bytes(byteorder="big", length=COMPRESSED_DIM_LEN)
        h = len(board[0]).to_bytes(byteorder="big", length=COMPRESSED_DIM_LEN)
        d.write(w)
        d.write(h)
        d.write(s.encode("latin"))


def loadCompressedBoard(filename):
    if not os.path.exists(filename):
        if os.path.exists(filename + ".boardC"):
            filename += ".boardC"
        else:
            raise FileNotFoundError

    with open(filename, "rb") as d:
        widthBin = d.read(COMPRESSED_DIM_LEN)
        heightBin = d.read(COMPRESSED_DIM_LEN)
        data = d.read()

    width = int.from_bytes(widthBin, byteorder="big", signed=False)
    height = int.from_bytes(heightBin, byteorder="big", signed=False)

    board = [[0 for _ in range(height)] for _ in range(width)]
    pos = 0
    maxPos = (width * height)
    for b in data.decode(encoding="latin"):
        decompressed = f"{ord(b):08b}"
        for val in decompressed:
            if pos >= maxPos:
                break
            x = pos % width
            y = pos // width
            board[x][y] = int(val)
            pos += 1
    return board


# ===== Image To Grid =====
def fromImageToSpecificSize(path, size=None, threshold=128):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Cannot read image")

    if size is not None:
        img = cv2.resize(img, size)
    w, h = img.shape
    grid = [[1 - (img[x][y] >= threshold) for x in range(w)] for y in range(h)]
    return grid


def fromImage(path, pixelPerCell=1, threshold=128):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Cannot read image")

    img = cv2.resize(img, dsize=None, fx=1 / pixelPerCell, fy=1 / pixelPerCell)
    w, h = img.shape
    grid = [[1 - (img[x][y] >= threshold) for x in range(w)] for y in range(h)]
    return grid


# ===== Static Functions =====
def createRandomBoard(width, height, rndThreshold=0.5):
    board = np.zeros((width, height))
    rnd = np.random.random((width, height))
    board[np.where(rnd < rndThreshold)] = 1
    return board


def emptyBoard(width, height):
    return np.zeros((width, height))


def checkEquals(board1, board2):
    return np.array_equal(board1, board2)


def addBorder(board, borderSize):
    w = len(board)
    h = len(board[0])
    w += 2 * borderSize
    h += 2 * borderSize
    newBoard = np.zeros((w, h))
    newBoard[borderSize:w - borderSize, borderSize:h - borderSize] = board
    return newBoard
