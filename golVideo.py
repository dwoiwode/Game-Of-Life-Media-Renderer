import os
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

from gol import GoL
import utils.colormaps as cm


class GoLVideo(GoL):
    def __init__(self, initBoard, width, height, countEdge=False, showNeighbourCount=False):
        super().__init__(initBoard=initBoard, countEdge=countEdge)
        self.canvasWidth = int(width)
        self.canvasHeight = int(height)
        self.showNeighbourCount = showNeighbourCount
        self.hightlights = []
        self.texts = []

    def record(self, filename,
               generations=100,
               fps=30,
               preview=False,
               colormap=None,
               colorReverse=False,
               showNeighbours=False,
               showGridlines=False,
               tl=(0, 0), br=(-1, -1), **kwargs):
        vidDuration = generations / fps
        print(f"#### GoL Settings ####\n"
              f"Board size: {self.width}x{self.height}\n"
              f"Generations: {generations}\n"
              f"\n"
              f"#### Video Settings ####\n"
              f"Filename: {filename}\n"
              f"Resolution: {self.canvasWidth}x{self.canvasHeight}\n"
              f"FPS: {fps}\n"
              f"Video duration: {vidDuration // 60:02.0f}:{vidDuration % 60:02.2f} mm:ss\n"
              # f"Colormap: {COLORMAPS[colormap]} {'(reveresed)' if colorReverse else ''}\n"
              f"Show Neighbours: {'enabled' if showNeighbours else 'disabled'}\n"
              f"Show Gridlines: {'enabled' if showGridlines else 'disabled'}\n"
              f"\n"
              f"Unknown options: {kwargs}")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        os.makedirs(Path(filename).parent, exist_ok=True)
        vidOut = cv2.VideoWriter(filename, fourcc, fps, (self.canvasWidth, self.canvasHeight), isColor=1)
        for i in tqdm(range(generations + 1)):
            img = self.renderImage(colormap=colormap, colorReverse=colorReverse, tl=tl, br=br,
                                   showNeighbours=showNeighbours, showGridlines=showGridlines)
            if preview:
                cv2.imshow(filename, img)
                cv2.setWindowTitle(filename, f"{filename} - Generation {self.generation}")
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            vidOut.write(img)

            self.step()
        vidOut.release()

    def recordImages(self, folder,
                     generations=100,
                     preview=False,
                     colormap=None,
                     colorReverse=False,
                     showNeighbours=False,
                     showGridlines=False,
                     tl=(0, 0), br=(-1, -1), **kwargs):
        print(f"#### GoL Settings ####\n"
              f"Board size: {self.width}x{self.height}\n"
              f"Generations: {generations}\n"
              f"\n"
              f"#### Video Settings ####\n"
              f"Folder: {folder}\n"
              f"Resolution: {self.canvasWidth}x{self.canvasHeight}\n"
              # f"Colormap: {COLORMAPS[colormap]} {'(reveresed)' if colorReverse else ''}\n"
              f"Show Neighbours: {'enabled' if showNeighbours else 'disabled'}\n"
              f"Show Gridlines: {'enabled' if showGridlines else 'disabled'}\n"
              f"\n"
              f"Unknown options: {kwargs}")
        os.makedirs(folder, exist_ok=True)
        for i in tqdm(range(generations + 1)):
            img = self.renderImage(colormap=colormap, colorReverse=colorReverse, tl=tl, br=br,
                                   showNeighbours=showNeighbours, showGridlines=showGridlines)

            if preview:
                cv2.imshow(folder, img)
                cv2.setWindowTitle(folder, f"{folder} - Generation {self.generation}")
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cv2.imwrite(f"{folder}/{self.name}{i:05d}.jpg", img)
            self.step()

    def renderImage(self, colormap=None, colorReverse=False, showNeighbours=False, showGridlines=False,
                    tl=(0, 0), br=(-1, -1)):
        img = np.zeros((self.canvasHeight, self.canvasWidth), dtype="B")

        xMin, yMin = tl
        xMax, yMax = br
        if xMax < 0:
            xMax += self.width
        if yMax < 0:
            yMax += self.height

        scaling = min(self.canvasWidth / (xMax - xMin + 1), self.canvasHeight / (yMax - yMin + 1))
        lastX = 0

        font = cv2.FONT_HERSHEY_PLAIN
        textScaling = 0.05
        if showNeighbours or len(self.texts) > 0:
            while max(cv2.getTextSize("0", font, textScaling, 1)[0]) < scaling * 0.9:
                textScaling += 0.05

        for x in range(xMin, xMax + 1):
            nextX = int((x + 1 - xMin) * scaling)
            lastY = 0
            for y in range(yMin, yMax + 1):
                nextY = int((y + 1 - yMin) * scaling)

                grayValue = 255 if self.getXY(x, y) else 0
                if showGridlines:
                    cv2.rectangle(img, (lastX, lastY), (nextX, nextY), 255, 2)

                if colorReverse:
                    grayValue = 255 - grayValue
                cv2.rectangle(img, (lastX, lastY), (nextX, nextY), grayValue, -1)
                lastY = nextY

                if showNeighbours:
                    nb = self.countNeighbours(x, y)
                    if nb == 0:
                        continue
                    textColor = [255 - grayValue for _ in range(3)]
                    actualNeighbours = nb - self.getXY(x, y)
                    cv2.putText(img, str(actualNeighbours), (int(lastX + 0.05 * scaling), int(lastY - 0.05 * scaling)),
                                font, textScaling, textColor, 1,
                                cv2.LINE_AA)
            lastX = nextX

        if colormap is None:
            return img

        channels = [cv2.LUT(img, colormap[:, i]) for i in range(3)]
        coloredImg = np.dstack(channels)
        for position, text, color in self.texts:
            tmp1, tmp2 = position
            x = int((tmp1 - xMin + 0.05) * scaling)
            y = int((tmp2 - yMin + 0.95) * scaling)
            cv2.putText(coloredImg, text, (x, y),
                        font, textScaling, color, 1,
                        cv2.LINE_AA)

        for position, color, strength in self.hightlights:
            tmp1, tmp2 = position
            try:
                x1, y1 = tmp1
                x2, y2 = tmp2
                x1 = int((x1 - xMin) * scaling)
                y1 = int((y1 - yMin) * scaling)
                x2 = int((x2 - xMin) * scaling)
                y2 = int((y2 - yMin) * scaling)
            except:
                x1 = int((tmp1 - xMin) * scaling)
                y1 = int((tmp2 - yMin) * scaling)
                x2 = int((tmp1 + 1 - xMin) * scaling)
                y2 = int((tmp2 + 1 - yMin) * scaling)
            cv2.rectangle(coloredImg, (x1, y1), (x2, y2), color, strength)
        return coloredImg

    def addHighlights(self, positions, color, strength=4):
        if isinstance(color, str):
            color = cm._htmlColor(color)
        for position in positions:
            self.hightlights.append((position, color,strength))

    def addText(self, position, text, color):
        if isinstance(color, str):
            color = cm._htmlColor(color)
        self.texts.append((position, text, color))


# COLORMAPS = {
#     cv2.COLORMAP_AUTUMN: "Autumn",
#     cv2.COLORMAP_BONE: "Bone",
#     cv2.COLORMAP_COOL: "Cool",
#     cv2.COLORMAP_HOT: "Hot",
#     cv2.COLORMAP_HSV: "HSV",
#     cv2.COLORMAP_JET: "Jet",
#     cv2.COLORMAP_OCEAN: "Ocean",
#     cv2.COLORMAP_PARULA: "Parula",
#     cv2.COLORMAP_PINK: "Ping",
#     cv2.COLORMAP_RAINBOW: "Rainbow",
#     cv2.COLORMAP_SPRING: "Spring",
#     cv2.COLORMAP_SUMMER: "Summer",
#     cv2.COLORMAP_WINTER: "Winter",
# }

if __name__ == '__main__':
    from utils import boardIO

    settings = {
        "generations": 29,
        "fps": 4,
        # "colormap": cm.getColorMapFor("DDFFDD", "ffffff"),
        "colormap": cm.getColorMapFor("298A08", "ffffff"),
        "colorReverse": False,
        "showNeighbours": True,
        "showGridlines": True,
        "tl": (0, 0),
        "br": (-1, -1)
    }

    k = 1
    board = boardIO.emptyBoard(10, 10)
    # board = boardIO.loadBoard(f"data/boards/10x10")

    # board = boardIO.loadBoard(f"data/boards/rules/Rule{i}")
    # board = pathToGrid("data/imgs/golTitle.png", (192*3, 108*3), threshold=128)
    # board = boardIO.loadBoard("data/boards/glider")
    # board = boardIO.loadBoard("data/boards/galaxy")
    golVid = GoLVideo(board, 540, 540, countEdge=False)
    black = "000000"
    darkRed = "E20338"
    # startImage = golVid.renderImage()
    # cv2.imshow("Initial Configuration", startImage)
    # cv2.waitKey(1)

    # golVid.record(f"data/videos/randomSmall/{i}.avi", **settings, preview=True)
    # 10x10
    golVid.board[0][7] = True
    golVid.board[1][7] = True
    golVid.board[1][9] = True
    golVid.board[2][7] = True
    golVid.board[2][8] = True

    # 3x3
    # golVid.board[0][0] = True
    # golVid.board[1][0] = True
    # golVid.board[1][2] = True
    # golVid.board[2][0] = True
    # golVid.board[2][1] = True

    # golVid.name = "10x10N_2Oszillator_Marked_"
    # golVid.addHighlights((((4,4),(5,7)),), darkRed)
    # golVid.addHighlights((((3,5),(6,6)),), darkRed)
    # golVid.recordImages(f"data/images/problems/", **settings, preview=False)
    golVid.reset()
    # settings["showNeighbours"] = False
    golVid.record(f"data/images/problems/glider.avi", **settings)
    # golVid.recordImages(f"data/images/infiniteGridN", **settings, preview=False)
