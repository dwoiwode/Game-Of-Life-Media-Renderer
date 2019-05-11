import random
import time
import tkinter as tk

DEPTH = 0
ENABLE_TIMEIT = False


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
    def __init__(self, width, height):
        self.root = tk.Tk("Game of life")
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.width = width
        self.height = height
        self.camTopLeft = [0.5, 0.5]
        self.camCellWidth = 10
        self.camZoomStep = 1 / 2000
        self.camOldDrag = None
        self.board = self.newBoard(random.random)
        self._canvasRectangles = [[self.canvas.create_rectangle((0, 0), (0, 0)) for _ in range(width)] for _ in
                                  range(height)]

        # Bindings
        self.root.bind("<Configure>", self.updateGrid)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)
        self.canvas.configure(cursor="hand1")
        self.updateCanvas()

    def zoom(self, event):
        self.camCellWidth *= 1 + event.delta * self.camZoomStep
        self.updateGrid()

    def on_start(self, event):
        self.camOldDrag = [event.x, event.y]

    def on_drag(self, event):
        x = event.x
        y = event.y
        if self.camOldDrag is not None:
            dx = self.camOldDrag[0] -x
            dy = self.camOldDrag[1]-y
            print(dx,dy)
            tlX, tlY = self.camTopLeft
            scalefactor = 1/self.camCellWidth
            self.camTopLeft = [tlX + dx*scalefactor, tlY + dy*scalefactor]
            self.updateGrid()
        self.camOldDrag = [x, y]
        pass

    def on_drop(self, event):
        self.camOldDrag = None

    def start(self):
        def stepLoop():
            self.step()
            self.root.after(10, stepLoop)

        self.root.after(10, stepLoop)
        self.root.mainloop()

    def newBoard(self, initValue: callable or int = 0):
        if initValue in (0, 1):
            return [[round(initValue) for _ in range(self.width)] for _ in range(self.height)]
        return [[round(initValue()) for _ in range(self.width)] for _ in range(self.height)]

    def updateCanvas(self):
        self.updateGrid()
        self.updateColors()

    @timeit
    def updateGrid(self, event=None):
        cw = self.camCellWidth
        tlX, tlY = self.camTopLeft
        for x in range(self.width):
            for y in range(self.height):
                rect = self._canvasRectangles[x][y]
                self.canvas.coords(rect, (x - tlX) * cw, (y - tlY) * cw, (x - tlX + 1) * cw, (y - tlY + 1) * cw)

    @timeit
    def updateColors(self):
        for x in range(self.width):
            for y in range(self.height):
                color = "black" if self.board[x][y] else "white"
                rect = self._canvasRectangles[x][y]
                currentColor = self.canvas.itemcget(rect, "fill")
                if color != currentColor:
                    self.canvas.itemconfigure(rect, fill=color)
                # self.canvas.create_rectangle((x * cellWidth, y * cellWidth), ((x + 1) * cellWidth, (y + 1) * cellWidth),
                #                              fill=color)

    @timeit
    def step(self, n=1):
        for i in range(n):
            self._singlestep()
        self.updateColors()

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

    def countNeighbors(self, x, y):
        sum_ = 0
        for i in range(3):
            for ii in range(3):
                try:
                    sum_ += self.board[x + i - 1][y + ii - 1]
                except IndexError:
                    pass
        return sum_


if __name__ == '__main__':
    gol = GoL(100, 100)
    gol.start()
