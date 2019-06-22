import os

import cv2
import numpy as np
from tqdm import tqdm

from gol import GoL


class GoLVideo(GoL):
    def __init__(self, initBoard, width, height, countEdge=False, showNeighbourCount=False):
        super().__init__(initBoard=initBoard, countEdge=countEdge)
        self.canvasWidth = int(width)
        self.canvasHeight = int(height)
        self.showNeighbourCount = showNeighbourCount

    def record(self, filename,
               generations=100,
               fps=30,
               preview=False,
               colormap=cv2.COLORMAP_BONE,
               colorReverse=False,
               showNeighbours=False,
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
              f"Colormap: {COLORMAPS[colormap]} {'(reveresed)' if colorReverse else ''}\n"
              f"Show Neighbours: {'enabled' if showNeighbours else 'disabled'}\n"
              f"\n"
              f"Unknown options: {kwargs}")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        vidOut = cv2.VideoWriter(filename, fourcc, fps, (self.canvasWidth, self.canvasHeight), isColor=1)
        for i in tqdm(range(generations + 1)):
            img = self.renderImage(colormap=colormap, colorReverse=colorReverse, tl=tl, br=br,
                                   showNeighbours=showNeighbours)
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
                     colormap=cv2.COLORMAP_BONE,
                     colorReverse=False,
                     showNeighbours=False,
                     tl=(0, 0), br=(-1, -1), **kwargs):
        print(f"#### GoL Settings ####\n"
              f"Board size: {self.width}x{self.height}\n"
              f"Generations: {generations}\n"
              f"\n"
              f"#### Video Settings ####\n"
              f"Folder: {folder}\n"
              f"Resolution: {self.canvasWidth}x{self.canvasHeight}\n"
              f"Colormap: {COLORMAPS[colormap]} {'(reveresed)' if colorReverse else ''}\n"
              f"Show Neighbours: {'enabled' if showNeighbours else 'disabled'}\n"
              f"\n"
              f"Unknown options: {kwargs}")
        os.makedirs(folder, exist_ok=True)
        for i in tqdm(range(generations + 1)):
            img = self.renderImage(colormap=colormap, colorReverse=colorReverse, tl=tl, br=br,
                                   showNeighbours=showNeighbours)

            cv2.imwrite(f"{folder}/{i:05d}.jpg", img)
            self.step()

    def renderImage(self, colormap=cv2.COLORMAP_BONE, colorReverse=False, showNeighbours=False,
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
        if showNeighbours:
            while max(cv2.getTextSize("0", font, textScaling, 1)[0]) < scaling * 0.9:
                textScaling += 0.05
            print(textScaling)

        for x in range(xMin, xMax + 1):
            nextX = int((x + 1 - xMin) * scaling)
            lastY = 0
            for y in range(yMin, yMax + 1):
                nextY = int((y + 1 - yMin) * scaling)
                grayValue = 255 if self.getXY(x, y) else 0
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

        colored = cv2.applyColorMap(img, colormap)
        return colored


COLORMAPS = {
    cv2.COLORMAP_AUTUMN: "Autumn",
    cv2.COLORMAP_BONE: "Bone",
    cv2.COLORMAP_COOL: "Cool",
    cv2.COLORMAP_HOT: "Hot",
    cv2.COLORMAP_HSV: "HSV",
    cv2.COLORMAP_JET: "Jet",
    cv2.COLORMAP_OCEAN: "Ocean",
    cv2.COLORMAP_PARULA: "Parula",
    cv2.COLORMAP_PINK: "Ping",
    cv2.COLORMAP_RAINBOW: "Rainbow",
    cv2.COLORMAP_SPRING: "Spring",
    cv2.COLORMAP_SUMMER: "Summer",
    cv2.COLORMAP_WINTER: "Winter",
}
if __name__ == '__main__':
    import boardIO

    settings = {
        "generations": 8,
        "fps": 3,
        "colormap": cv2.COLORMAP_BONE,
        "colorReverse": False,
        "showNeighbours": False,
        "tl": (0, 0),
        "br": (-1, -1)
    }
    # board = GoL.createRandomBoard(192, 108)
    # board = pathToGrid("data/imgs/golTitle.png", (192*3, 108*3), threshold=128)
    # board = boardIO.loadBoard("data/boards/Rules/birth1")
    board = boardIO.loadBoard("data/boards/galaxy")
    golVid = GoLVideo(board, 1080, 1080, countEdge=False)
    startImage = golVid.renderImage()
    cv2.imshow("Initial Configuration", startImage)
    cv2.waitKey(1)

    golVid.record("galaxy.avi", **settings, preview=True)
    # golVid.recordImages("data/images/galaxy", **settings, preview=True)
