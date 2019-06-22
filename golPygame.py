import datetime
import time

import math
import pygame

from gol import timeit, GoL

pygame.init()
pygame.font.init()

# === Black/White ===
COLOR_MOUSE = (255, 0, 0)
COLOR_OFF = (00, 0, 0)
COLOR_ON = (255, 255, 255)
COLOR_BG = (0, 0, 0)
COLOR_HIST = (255, 255, 255)


# === Black/Green ===
# COLOR_MOUSE = (255, 128, 0)
# COLOR_OFF = (20, 20, 20)
# COLOR_ON = (0, 255, 0)
# COLOR_HIST = (255, 128, 128)
# COLOR_BG = (0, 0, 0)


class GoLPygame(GoL):
    def __init__(self, initBoard=None):
        super().__init__(initBoard)
        size = (900, 900)
        self.canvas = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Game of Life")
        assert isinstance(self.canvas, pygame.Surface)
        self.camTopLeft = [0, 0]
        self.camCellWidth = 10
        self.camZoomStep = 0.5
        self.camOldDrag = None
        self.simulate = False
        self.done = False
        self.latestManualTile = None
        self.lastupdate = 0

        # Settings
        self.boardName = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        self.drawNeighbors = False
        self.delay = 0.1
        self.record = False
        self.showHistory = False

    @timeit
    def updateCanvas(self):
        # Clear board
        self.canvas.fill(COLOR_BG)

        # Draw cells
        cw = self.camCellWidth
        _, _, w, h = self.canvas.get_rect()
        neighboursFont = pygame.font.SysFont('Arial', int(cw))
        tlX, tlY = self.camTopLeft
        minX = max(0, int(tlX))
        minY = max(0, int(tlY))
        maxX = min(int(minX + w / cw) + 2, self.width)
        maxY = min(int(minY + h / cw) + 2, self.height)
        # for x in range(minX, maxX):
        #     for y in range(minY, maxY):
        for x in range(0, maxX):
            for y in range(0, maxY):
                if self.getXY(x, y):
                    on = COLOR_ON
                    off = COLOR_OFF
                else:
                    on = COLOR_OFF
                    off = COLOR_ON
                    if self.showHistory:
                        on = [self.oldBoard[x][y] * COLOR_HIST[i] for i in range(3)]
                curTlX, curTlY = (x - tlX) * cw, (y - tlY) * cw

                pygame.draw.rect(self.canvas, on,
                                 (curTlX, curTlY, cw, cw))

                if self.drawNeighbors:
                    nb = self.countNeighbours(x, y)
                    if nb == 0:
                        continue
                    txt = neighboursFont.render(str(nb - self.getXY(x, y)), False, off)
                    _, _, txtW, txtH = txt.get_rect()
                    offsetX = (cw - txtW) / 2
                    offsetY = (cw - txtH) / 2
                    self.canvas.blit(txt, (curTlX + offsetX - 1, curTlY + offsetY - 1))

        # Draw mouse position
        x, y = pygame.mouse.get_pos()
        boardX, boardY = self.screenToBoard(x, y)
        if boardX is not None and boardY is not None:
            curTlX, curTlY = (boardX - tlX) * cw, (boardY - tlY) * cw
            pygame.draw.rect(self.canvas, COLOR_MOUSE, (curTlX - 1, curTlY - 1, cw - 2, cw - 2), 1)

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
            self.updateCanvas()

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
        if event.button in [4, 5]:  # Scrolling
            self.zoom(event)
        elif event.button == 1:  # Leftclick
            self.toggleManual(x, y, True)
        elif event.button == 3:  # Rightclick
            self.toggleManual(x, y, False)

    def mouseUP(self, event):
        if event.button == 2:  # Middleclick
            self.resetDrag()

    def mouseMove(self, event):
        x, y = event.pos
        if event.buttons[1]:  # Middleclick
            self.drag(x, y)
        elif event.buttons[0]:  # Leftclick
            self.toggleManual(x, y, True)
        elif event.buttons[2]:  # Rightclick
            self.toggleManual(x, y, False)

    def keyDown(self, event):
        pass

    def keyUp(self, event):
        key = event.key
        c = chr(event.key)
        print(c)
        if c == "p":  # Pause
            self.togglePause()
        elif c == "n":  # Toggle Numbers
            self.toggleNumberNeighbors()
        elif c == "c":  # Clear
            self.clearBoard()
        elif c == "q":
            pygame.quit()
        elif c == "h":
            self.showHistory = not self.showHistory
        elif c == "s":
            self.step()
            self.updateCanvas()
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
        before = self.screenToBoard(*pos)
        self.camCellWidth *= 1 + (4.5 - event.button) * self.camZoomStep
        pos = pygame.mouse.get_pos()
        after = self.screenToBoard(*pos)
        print(f"{before} ->  {after} ({self.camCellWidth})")

    def adjustDelay(self, factor):
        self.delay *= factor

    def toggleManual(self, screenX, screenY, newState=None):
        boardX, boardY = self.screenToBoard(screenX, screenY)
        if self.latestManualTile != (boardX, boardY):
            if None in (boardX, boardY):
                return
            if newState is None:
                newState = 1 - self.getXY(boardX, boardY)  # Toggle
            self.setXY(boardX, boardY, int(newState))

            self.latestManualTile = (boardX, boardY)

    def drag(self, x, y):
        if self.camOldDrag is not None:
            dx = self.camOldDrag[0] - x
            dy = self.camOldDrag[1] - y
            tlX, tlY = self.camTopLeft
            scalefactor = 1 / self.camCellWidth
            self.camTopLeft = [tlX + dx * scalefactor, tlY + dy * scalefactor]
        self.camOldDrag = (x, y)

    def resetDrag(self):
        self.camOldDrag = None

    def screenToBoard(self, screenX, screenY):
        tlX, tlY = self.camTopLeft
        cw = self.camCellWidth
        x, y = int(screenX / cw + tlX), int(screenY / cw + tlY)
        if not (0 <= x < self.width):
            x = None
        if not (0 <= y < self.height):
            y = None
        return x, y



if __name__ == '__main__':
    path = "data/imgs/golTitle.png"
    size = (16, 9)
    size = tuple([s * 30 for s in size])
    grid = pathToGrid(path, size)
    gol = GoLPygame(*size, initBoard=grid)
    gol.start()
