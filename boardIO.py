from pathlib import Path
import os

CHAR_ON = "X"
CHAR_OFF = "_"
CHAR_DELIMITER = "\n"
COMPRESSED_DIM_LEN = 3  # 3 => Maxsize = 256^3 - 1 = 16_777_215


def saveBoard(board, filename):
    s = CHAR_DELIMITER.join(
        "".join(
            CHAR_ON if board[x][y] else CHAR_OFF
            for x in range(len(board))
        )
        for y in range(len(board[0]))
    )
    os.makedirs(Path(filename).parent, exist_ok=True)
    with open(filename, "w") as d:
        d.write(CHAR_OFF+CHAR_ON+CHAR_DELIMITER)
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

def saveCompressedBoard(board, filename):
    # singleBinString = "".join("".join("1" if board[x][y] else "0" for x in range(len(board)) for y in range(len(board[0]))))
    singleBinString = "".join("".join("1" if board[x][y] else "0" for x in range(len(board))) for y in range(len(board[0])))

    # singleBinString = ""
    # for y in range(len(board[0])):
    #     for x in range(len(board)):
    #         if board[x][y]:
    #             c = "1"
    #         else:
    #             c = "0"
    #         singleBinString += c

    singleBinString += (8 - len(singleBinString) % 8) * "0"
    # s = "".join(chr(int(singleBinString[i * 8:(i + 1) * 8], 2)) for i in range(len(singleBinString) // 8))
    s = ""
    for i in range(len(singleBinString) // 8):
        s += chr(int(singleBinString[i * 8:(i + 1) * 8], 2))

    os.makedirs(Path(filename).parent, exist_ok=True)
    with open(filename, "wb") as d:
        # print(f"Save: w,h: {len(board)}x{len(board[0])}")
        w = len(board).to_bytes(byteorder="big", length=COMPRESSED_DIM_LEN)
        h = len(board[0]).to_bytes(byteorder="big", length=COMPRESSED_DIM_LEN)
        # print(f"Save: w,h Bytes: {w}x{h}")
        d.write(w)
        d.write(h)
        d.write(s.encode("latin"))

def loadCompressedBoard(filename):
    def bytesToInt(bs):
        n = int.from_bytes(bs, byteorder="big", signed=False)
        return n


    if not os.path.exists(filename):
        if os.path.exists(filename + ".boardC"):
            filename += ".boardC"
        else:
            raise FileNotFoundError

    with open(filename, "rb") as d:
        widthBin = d.read(COMPRESSED_DIM_LEN)
        heightBin = d.read(COMPRESSED_DIM_LEN)
        data = d.read()

    # print(f"Load: w,h Bytes: {widthBin}x{heightBin}")
    width = bytesToInt(widthBin)
    height = bytesToInt(heightBin)
    # print(f"Load: w,h: {width}x{height}")

    # Full board
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

    # Empty board
    # board = []
    # pos = 0
    # oldY = 0
    # row = []
    # maxPos = (width * height)
    # for b in data.decode(encoding="latin"):
    #     decompressed = f"{ord(b):08b}"
    #     for val in decompressed:
    #         if pos >= maxPos:
    #             break
    #         y = pos // width
    #         if y != oldY:
    #             board.append(row)
    #             row = []
    #             oldY = y
    #         row.append(int(val))
    #         pos += 1
    # board.append(row)
    return board

def checkEquals(board1, board2):
    from sys import stderr
    if len(board1) != len(board2) or len(board1[0]) != len(board2[0]):
        print(f"Invalid lengths! {len(board1)}x{len(board1[0])} != {len(board2)}x{len(board2[0])}", file=stderr)
        return False
    for y in range(len(board1[0])):
        for x in range(len(board1)):
            if board1[x][y] != board2[x][y]:
                print(f"Field inconsistent at pos ({x},{y}): {board1[x][y]} != {board2[x][y]}", file=stderr)
                return False
    return True


if __name__ == '__main__':
    import gol
    gol.ENABLE_TIMEIT = True

    filename = "data/boards/test.board"
    filenameCompressed = "data/boards/test.boardC"

    print("Create Board")
    originalBoard = gol.GoL.createRandomBoard(1500, 1500)
    # originalBoard = loadBoard(filename)

    print("Save Board")
    saveBoard(originalBoard, filename)

    print("Save Board Compressed")
    saveCompressedBoard(originalBoard, filenameCompressed)

    print("Load Board")
    loadedBoard = loadBoard(filename)

    print("Load Board Compressed")
    loadedCompressedBoard = loadCompressedBoard(filenameCompressed)

    print("Check Boards")
    if checkEquals(originalBoard, loadedBoard):
        print(" > Normal Boards equal")

    print("Check Boards Compressed")
    if checkEquals(originalBoard, loadedCompressedBoard):
        print(" > Compressed Boards equal")

    uncompressedSize = os.path.getsize(filename)
    compressedSize = os.path.getsize(filenameCompressed)
    print(f"Uncompressed size: {uncompressedSize:10d} bytes\n"
          f"Compressed size:   {compressedSize:10d} bytes\n"
          f"Compression rate: {compressedSize / uncompressedSize * 100:.2f}%")
