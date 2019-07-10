import os
import re
from pathlib import Path

import cv2
import numpy as np

# Default chars used when saving boards
from tqdm import tqdm

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

    if "." not in filename:
        filename += ".board"
    os.makedirs(Path(filename).parent, exist_ok=True)
    with open(filename, "w") as d:
        d.write(off + on + delimiter)
        d.write(s)


def loadBoard(filename):
    filename = _checkFileExists(filename, ".board")

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
                raise ValueError(f"Invalid char at ({x},{y}): {data[x][y]}")
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

    if "." not in filename:
        filename += ".boardC"
    os.makedirs(Path(filename).parent, exist_ok=True)
    with open(filename, "wb") as d:
        w = len(board).to_bytes(byteorder="big", length=COMPRESSED_DIM_LEN)
        h = len(board[0]).to_bytes(byteorder="big", length=COMPRESSED_DIM_LEN)
        d.write(w)
        d.write(h)
        d.write(s.encode("latin"))


def loadCompressedBoard(filename):
    filename = _checkFileExists(filename, ".boardC")

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


# === RLE ===
# Run-length encoded. Simple Algorithm used by golly
# Run-length encoding is a simple (but not very efficient) method of file compression.
# In Life the term refers to a specific ASCII encoding used for patterns in Conway's Life and other similar cellular automata.
# This encoding was introduced by Dave Buckingham and is now the usual means of exchanging relatively
# small patterns by email or in online forum discussions.
# The "run lengths" are the numbers, b's are dead cells, o's are live cells, and dollar signs signal new lines:
def saveRLE(board, filename):
    pass


def loadRLE(filename):
    filename = _checkFileExists(filename, ".rle")
    with open(filename, "r") as d:
        line = "#"
        while line.startswith("#"):
            line = d.readline()   # Reads one more line than needed. This line contains position and rules
        data = d.read()

    data = data.replace("\n", "")  # Linebreaks are irrelevant
    data = data.split("!")[0]  # End of file
    lines = data.split("$")
    del data
    countings = [map(lambda s: int(s) if s != "" else 1, re.split("[ob]", line)) for line in lines]
    w = max([sum(row) for row in countings])
    h = len(countings)
    del countings

    print("Width:", w, "Height:", h)
    board = emptyBoard(w, h)
    alreadyParsedLines = dict()
    for i, line in tqdm(enumerate(lines),desc="Loading RLE", total=h):
        if line in alreadyParsedLines:
            board[:, i] = alreadyParsedLines[line]
            # print("Used Cache (",i,")")
            continue

        # if not i % 5000:
        #     print(f"RLE Loading line: {i}/{h} ({i / h * 100:.2f}%)")
        parsedRow = np.array([0 for _ in range(w)])
        curN = ""
        sumRow = 0
        for c in line:
            if c == "o" or c == "b":
                n = int(curN) if curN != "" else 1
                if c == "o":
                    parsedRow[sumRow:sumRow + n] = 1
                sumRow += n
                curN = ""
                continue
            curN += c
        alreadyParsedLines[line] = parsedRow
        board[:, i] = parsedRow
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
def emptyBoard(width, height):
    return np.zeros((width, height))


def createRandomBoard(width, height, rndThreshold=0.5):
    board = emptyBoard(width, height)
    rnd = np.random.random((width, height))
    board[np.where(rnd < rndThreshold)] = 1
    return board


def checkEquals(board1, board2):
    return np.array_equal(board1, board2)


def addBorder(board, borderSize):
    return np.pad(board, pad_width=borderSize, mode='constant', constant_values=0)


def _checkFileExists(filename, ending):
    if not os.path.exists(filename):
        if os.path.exists(filename + ending):
            filename += ending
        else:
            raise FileNotFoundError
    return filename
