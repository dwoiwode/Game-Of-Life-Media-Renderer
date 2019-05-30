import cv2
import numpy as np
from tqdm import tqdm

from gol import GoL
from imgToGrid import pathToGrid


class GoLVideo(GoL):
    def __init__(self, initBoard, width, height, countEdge=False, showNeighbourCount=False):
        super().__init__(len(initBoard), len(initBoard[0]), initBoard=initBoard, countEdge=countEdge)
        self.canvasWidth = int(width)
        self.canvasHeight = int(height)
        self.showNeighbourCount = showNeighbourCount

    def record(self, filename, generations=100, fps=30, preview=False, colormap=cv2.COLORMAP_BONE, colorReverse=False):
        vidDuration = generations / fps
        print(f"#### GoL Settings ####\n"
              f"Board size: {self.width}x{self.height}\n"
              f"Generations: {generations}\n"
              f"\n\n"
              f"#### Video Settings ####\n"
              f"Filename: {filename}\n"
              f"Resolution: {self.canvasWidth}x{self.canvasHeight}\n"
              f"FPS: {fps}\n"
              f"Video duration: {vidDuration // 60:02.0f}:{vidDuration % 60:02.2f} mm:ss\n"
              f"Colormap: {COLORMAPS[colormap]} {'(reveresed)' if colorReverse else ''}\n"
              f"")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        vidOut = cv2.VideoWriter(filename, fourcc, fps, (self.canvasWidth, self.canvasHeight), isColor=1)
        for i in tqdm(range(generations)):
            img = self.renderImage(colormap=colormap, colorReverse=colorReverse)
            if preview:
                cv2.imshow(filename, img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            vidOut.write(img)
            self.step()
        vidOut.release()
        cv2.destroyAllWindows()

    def renderImage(self, colormap=cv2.COLORMAP_BONE, colorReverse=False):
        img = np.zeros((self.canvasHeight, self.canvasWidth), dtype="B")
        scaling = min(self.canvasWidth / self.width, self.canvasHeight / self.height)
        # scaling = min(self.width / self.canvasWidth, self.height / self.canvasHeight)
        lastX = 0
        for x in range(self.width):
            nextX = int((x + 1) * scaling)
            lastY = 0
            for y in range(self.height):
                nextY = int((y + 1) * scaling)
                # if self.board[x][y]:
                grayValue = 255 if self.board[x][y] else 0
                if colorReverse:
                    grayValue = 255 - grayValue
                cv2.rectangle(img, (lastX, lastY), (nextX, nextY), grayValue, -1)
                lastY = nextY
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
    # board = GoL.createRandomBoard(192, 108)
    board = pathToGrid("data/imgs/golTitle.png", (192*2, 108*2), threshold=128)
    golVid = GoLVideo(board, 1920, 1080, countEdge=False)
    startImage = golVid.renderImage()
    cv2.imshow("Initial Configuration", startImage)
    golVid.record("test.avi", generations=2000, fps=24, preview=True, colormap=cv2.COLORMAP_BONE, colorReverse=True)
