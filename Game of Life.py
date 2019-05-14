import random
import time

import pygame

pygame.init()
pygame.font.init()

DEPTH = 0
ENABLE_TIMEIT = False

# === Black/White ===
# COLOR_MOUSE = (255, 0, 0)
# COLOR_OFF = (20, 20, 20)
# COLOR_ON = (255, 255, 255)
# COLOR_BG = (0, 0, 0)


# === Black/Green ===
COLOR_MOUSE = (255, 128, 0)
COLOR_OFF = (20, 20, 20)
COLOR_ON = (0, 255, 0)
COLOR_BG = (0, 0, 0)


def timeit(func):
    def wrapped(*args, **kwargs):
        global DEPTH
        t1 = time.time()
        DEPTH += 1
        ret = func(*args, **kwargs)
        DEPTH -= 1
        t2 = time.time()
        if ENABLE_TIMEIT:
            print(f"[{t2:.20f}]{DEPTH * '  '}[{func.__name__}] Took {t2 - t1} seconds")
        return ret

    return wrapped


class GoL:
    def __init__(self, width, height, init=None):
        size = (900, 900)
        self.canvas = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Game of Life")
        assert isinstance(self.canvas, pygame.Surface)
        self.width = width
        self.height = height
        self.camTopLeft = [0, 0]
        self.camCellWidth = 10
        self.camZoomStep = 0.5
        self.camOldDrag = None
        self.board = self.newBoard(random.random)
        # self.board = self.newBoard()
        self.simulate = True
        self.done = False
        self.latestManualTile = None

        # Settings
        self.drawNeighbors = False

    def start(self):
        while not self.done:
            # Events
            self.eventHandling()

            # Execution
            if self.simulate:
                self.step()

            # Update
            self.updateCanvas()
        pygame.quit()

    # Event bindings
    def eventHandling(self):
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
        c = chr(event.key)
        if c == "p":  # Pause
            self.togglePause()
        elif c == "n":  # Toggle Numbers
            self.toggleNumberNeighbors()
        elif c == "c":  # Clear
            self.clearBoard()
        elif c == "q":
            pygame.quit()

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

    @timeit
    def updateCanvas(self):
        # Clear board
        self.canvas.fill(COLOR_BG)

        # Draw cells
        cw = self.camCellWidth
        _, _, w, h = self.canvas.get_rect()
        neighborsFont = pygame.font.SysFont('Arial', int(cw))
        tlX, tlY = self.camTopLeft
        minX = max(0, int(tlX))
        minY = max(0, int(tlY))
        maxX = min(int(minX + w / cw) + 2, self.width)
        maxY = min(int(minY + h / cw) + 2, self.height)
        for x in range(minX, maxX):
            for y in range(minY, maxY):
                if self.board[x][y]:
                    on = COLOR_ON
                    off = COLOR_OFF
                else:
                    on = COLOR_OFF
                    off = COLOR_ON
                curTlX, curTlY = (x - tlX) * cw, (y - tlY) * cw
                pygame.draw.rect(self.canvas, on,
                                 (curTlX - 1, curTlY - 1, cw - 2, cw - 2))

                if self.drawNeighbors:
                    nb = self.countNeighbors(x, y)
                    if nb == 0:
                        continue
                    txt = neighborsFont.render(str(nb - self.board[x][y]), False, off)
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

        pygame.display.update()

    @timeit
    def step(self, n=1):
        for i in range(n):
            self._singlestep()

    @timeit
    def _singlestep(self):
        def getValue(x, y):
            neighbors = self.countNeighbors(x, y)
            if neighbors == 3:
                return 1
            elif neighbors == 4:
                return self.board[x][y]
            else:
                return 0

        board = self.newBoard()
        for x in range(self.width):
            for y in range(self.height):
                board[x][y] = getValue(x, y)
        self.board = board

    def toggleManual(self, screenX, screenY, newState=None):
        boardX, boardY = self.screenToBoard(screenX, screenY)
        if self.latestManualTile != (boardX, boardY):
            if None in (boardX, boardY):
                return
            if newState is None:
                newState = 1 - self.board[boardX][boardY]  # Toggle
            self.board[boardX][boardY] = int(newState)

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

    def clearBoard(self):
        self.board = self.newBoard()

    def countNeighbors(self, x, y):
        sum_ = 0
        for i in range(3):
            for ii in range(3):
                try:
                    sum_ += self.board[x + i - 1][y + ii - 1]
                except IndexError:
                    pass
        return sum_

    def newBoard(self, initValue: callable or int = 0):
        if initValue in (0, 1):
            return [[round(initValue) for _ in range(self.height)] for _ in range(self.width)]
        return [[round(initValue()) for _ in range(self.height)] for _ in range(self.width)]


if __name__ == '__main__':
    gol = GoL(128, 64)
    gol.start()
