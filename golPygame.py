import datetime
import time

import math
import pygame

import utils.colormaps as cm
from gol import timeit, GoL
from utils import boardIO

pygame.init()
pygame.font.init()

# === Black/White ===
COLOR_MOUSE = cm._htmlColor("#A400FF", rgb=True)
COLOR_BG = (0, 0, 0)


# === Black/Green ===
# COLOR_MOUSE = (255, 128, 0)
# COLOR_OFF = (20, 20, 20)
# COLOR_ON = (0, 255, 0)
# COLOR_HIST = (255, 128, 128)
# COLOR_BG = (0, 0, 0)

class DRAW:
    NONE, ADD, REMOVE = range(3)


class GoLPygame(GoL):
    def __init__(self, initBoard=None, colormap=cm.COLORMAP_BLACK_WHITE):
        super().__init__(initBoard)
        size = (900, 900)
        self.canvas = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Game of Life")
        assert isinstance(self.canvas, pygame.Surface)
        self.camTopLeft = (0, 0)
        self.camCellWidth = max(size[0] / self.width, size[1] / self.height)
        self.neighboursFont = None
        self._updateNeighboursFont()
        self.camZoomStep = 0.5
        self.camOldDrag = None
        self.simulate = False
        self.done = False
        self.latestManualTile = None
        self.isRunningBeforeDraw = False
        self.lastupdate = 0
        self.drawMode = DRAW.NONE

        # Settings
        self.boardName = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        self.drawNeighbors = False
        self.drawGridlines = True
        self.delay = 0.00001
        self.record = False
        self.showHistory = False
        self.colorMap = colormap
        # print(colormap[0][0])

    @timeit
    def updateCanvas(self):
        # Clear board
        self.canvas.fill(COLOR_BG)

        # Draw cells
        cw = self.camCellWidth
        _, _, w, h = self.canvas.get_rect()
        tlX, tlY = self.camTopLeft
        minX = max(0, int(tlX))
        minY = max(0, int(tlY))
        maxX = min(int(minX + w / cw) + 2, self.width)
        maxY = min(int(minY + h / cw) + 2, self.height)
        for x in range(minX, maxX):
            for y in range(minY, maxY):
                # for x in range(0, maxX):
                #     for y in range(0, maxY):
                if self.getXY(x, y):
                    on = self.colorMap[-1]
                    off = self.colorMap[0]
                else:
                    on = self.colorMap[0]
                    off = self.colorMap[-1]
                    if self.showHistory:
                        on = self.colorMap[int(self.oldBoard[x][y] * 255)]

                self.drawRect(x, y, on)
                if self.drawGridlines:
                    self.drawRect(x, y, self.colorMap[-1], max(1, self.camCellWidth * 0.05))

                if self.drawNeighbors:
                    nb = self.countNeighbours(x, y)
                    if nb == 0:
                        continue
                    self.drawText(int(nb - self.getXY(x, y)), x, y, off)

        # Draw mouse position
        x, y = pygame.mouse.get_pos()
        boardX, boardY = self.screenToBoard(x, y)
        if boardX is not None and boardY is not None:
            self.drawRect(boardX, boardY, COLOR_MOUSE, width=max(1, self.camCellWidth * 0.1))

        # Draw Flags
        if self.record:
            print("Recording")

        pygame.display.update()

    def saveScreenshot(self):
        pygame.image.save(self.canvas, "data/img.jpg")

    def start(self):
        while not self.done:
            # Events
            self._eventHandling()

            # Execution
            if self.simulate and (time.time() - self.lastupdate) > self.delay:
                self.lastupdate = time.time()
                self.step()

            # Update
            try:
                self.updateCanvas()
            except pygame.error:
                pass

            # Record
            if self.record:
                self.saveScreenshot()

        pygame.quit()

        # Event bindings

    def _eventHandling(self):
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.MOUSEMOTION:
                self.mouseMove(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouseDown(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouseUP(event)
            elif event.type == pygame.KEYDOWN:
                self.keyDown(event)
            elif event.type == pygame.KEYUP:
                self.keyUp(event)
            elif event.type == pygame.VIDEORESIZE:
                self.resize(event)

    def mouseDown(self, event):
        x, y = event.pos
        if event.button in [pygame.BUTTON_WHEELDOWN, pygame.BUTTON_WHEELUP]:  # Scrolling
            # if pygame.KMOD_CTRL & pygame.key.get_mods():
            self.zoom(event)
        elif event.button == pygame.BUTTON_LEFT:
            self.isRunningBeforeDraw = self.simulate
            self.simulate = False
            if self.getXY(*self.screenToBoard(x, y)):
                self.drawMode = DRAW.REMOVE
            else:
                self.drawMode = DRAW.ADD
            if pygame.KMOD_SHIFT & pygame.key.get_mods():
                self.latestManualTile = self.shiftManualTile
                self.drawMode = DRAW.ADD
            self.toggleManual(x, y, self.drawMode == DRAW.ADD)

    def mouseUP(self, event):
        if event.button == pygame.BUTTON_MIDDLE:
            self.resetDrag()
        if event.button == pygame.BUTTON_LEFT:
            self.resetDraw()

    def mouseMove(self, event):
        x, y = event.pos
        if event.buttons[1]:  # Middleclick
            self.drag(x, y)
        elif event.buttons[0]:  # Leftclick
            self.toggleManual(x, y, self.drawMode == DRAW.ADD)

    def keyDown(self, event):
        pass

    def keyUp(self, event):
        key = event.key
        c = chr(key)
        # print(c)
        if c == "\r":  # Pause
            self.togglePause()
        elif c == "n":  # Toggle Numbers
            self.toggleNumberNeighbors()
        elif c == "c":  # Clear
            self.clear()
        elif c == "q":
            pygame.quit()
        elif c == "g":
            self.drawGridlines = not self.drawGridlines
        elif c == "h":
            self.showHistory = not self.showHistory
        elif c == " ":
            self.step()
            self.updateCanvas()
        elif c == "w":
            boardIO.saveBoard(self.board, f"data/boards/saving/{self.boardName}_{self.generation:05d}")
        elif c == "r":
            self.initRandom()
        elif c == "]":  # Plus
            self.adjustDelay(1 / math.sqrt(10))
        elif c == "/":  # Minus
            self.adjustDelay(math.sqrt(10))

    def resize(self, event):
        assert isinstance(self.canvas, pygame.Surface)
        self.canvas = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        # Other functions

    def togglePause(self):
        self.simulate = not self.simulate

    def toggleNumberNeighbors(self):
        self.drawNeighbors = not self.drawNeighbors

    def zoom(self, event):
        pos = pygame.mouse.get_pos()

        before = self.screenToBoard(*pos, withNegative=True)
        tlX, tlY = self.camTopLeft
        dX, dY = before[0] - tlX, before[1] - tlY
        dX *= self.camCellWidth
        dY *= self.camCellWidth
        self.camCellWidth *= 1 + (4.5 - event.button) * self.camZoomStep
        dX /= self.camCellWidth
        dY /= self.camCellWidth
        self.camTopLeft = before[0] - dX, before[1] - dY

        self._updateNeighboursFont()

    def adjustDelay(self, factor):
        self.delay *= factor

    def toggleManual(self, screenX, screenY, newState=None):
        newState = int(newState)
        boardX, boardY = self.screenToBoard(screenX, screenY)
        if self.latestManualTile != (boardX, boardY):
            if None in (boardX, boardY):
                return
            if newState is None:
                newState = 1 - self.getXY(boardX, boardY)  # Toggle

            self.setXY(boardX, boardY, newState)
            if self.latestManualTile is not None:
                latestBoardX, latestBoardY = self.latestManualTile
                distX = boardX - latestBoardX
                distY = boardY - latestBoardY
                dist = (distX * distX + distY * distY) ** 0.5
                n_points = int(dist)
                facX = distX / n_points
                facY = distY / n_points
                for i in range(1, n_points):
                    newX = latestBoardX + facX * i
                    newY = latestBoardY + facY * i
                    self.setXY(int(newX), int(newY), int(newState))

            self.latestManualTile = (boardX, boardY)

    def drag(self, x, y):
        if self.camOldDrag is not None:
            dx = self.camOldDrag[0] - x
            dy = self.camOldDrag[1] - y
            tlX, tlY = self.camTopLeft
            scalefactor = 1 / self.camCellWidth
            self.camTopLeft = (tlX + dx * scalefactor, tlY + dy * scalefactor)
        self.camOldDrag = (x, y)

    def resetDrag(self):
        self.camOldDrag = None

    def resetDraw(self):
        self.shiftManualTile = self.latestManualTile
        self.latestManualTile = None
        self.simulate = self.isRunningBeforeDraw

    def screenToBoard(self, screenX, screenY, withNegative=False):
        tlX, tlY = self.camTopLeft
        cw = self.camCellWidth
        x, y = int(screenX / cw + tlX), int(screenY / cw + tlY)
        if not (0 <= x < self.width) and not withNegative:
            x = None
        if not (0 <= y < self.height) and not withNegative:
            y = None
        return x, y

    def drawRect(self, x, y, color, width=0):
        tlX, tlY = self.camTopLeft
        cw = self.camCellWidth
        curTlX, curTlY = (x - tlX) * cw, (y - tlY) * cw
        pygame.draw.rect(self.canvas, color, (curTlX, curTlY, cw + 1, cw + 1), int(width))

    def drawText(self, text, x, y, color):
        tlX, tlY = self.camTopLeft
        cw = self.camCellWidth
        curTlX, curTlY = (x - tlX) * cw, (y - tlY) * cw

        txt = self.neighboursFont.render(str(text), False, color)
        _, _, txtW, txtH = txt.get_rect()
        offsetX = (cw - txtW) / 2
        offsetY = (cw - txtH) / 2
        self.canvas.blit(txt, (curTlX + offsetX - 1, curTlY + offsetY - 1))

    def _updateNeighboursFont(self):
        self.neighboursFont = pygame.font.SysFont('Arial', int(self.camCellWidth))

    def clear(self):
        self.clearBoard()
        self.simulate = False


if __name__ == '__main__':
    board = boardIO.emptyBoard(100, 100)
    # board = boardIO.loadRLE("data/boards/metapixel-on-off.rle")
    # board = boardIO.loadRLE("data/boards/randomStill")
    # board = boardIO.loadBoard("data/boards/10x10")
    # board = boardIO.fromImage("data/imgs/qr_github.png",pixelPerCell=8)
    # board = boardIO.fromImageToSpecificSize("data/imgs/qr_github2.png", size=(25, 25))
    # board = boardIO.addBorder(board, 40)
    gol = GoLPygame(initBoard=board, colormap=cm.COLORMAP_WHITE_GREEN)
    gol.start()
