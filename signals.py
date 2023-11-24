import numpy as np
from multiprocessing import Lock

from basicTypes import Coord
from grid import visitNeighborhood

SIGNAL_MIN = 0
SIGNAL_MAX = 255  # equivalent to UINT8_MAX in C++

class Signals:
    def __init__(self):
        self.data = None
        self.lock = Lock()

    def init(self, numLayers, sizeX, sizeY):
        self.data = np.zeros((numLayers, sizeX, sizeY), dtype=np.uint16)

    def getMagnitude(self, layerNum, loc: Coord):
        return self.data[layerNum, loc.x, loc.y]

    def increment(self, layerNum, loc: Coord):
        centerIncreaseAmount = 2
        neighborIncreaseAmount = 1
        radius = 1.5

        with self.lock:
            # Increase the neighbors
            visitNeighborhood(loc, radius, lambda loc: self.increase(layerNum, loc, neighborIncreaseAmount))

            # Increase the center cell
            self.increase(layerNum, loc, centerIncreaseAmount)

    def increase(self, layerNum, loc: Coord, amount: int):
        # amount >= 0
        self.data[layerNum, loc.x, loc.y] = min(255, self.data[layerNum, loc.x, loc.y] + amount)

    def zeroFill(self):
        self.data.fill(0)

    def fade(self, layerNum):
        fadeAmount = 1

        for x in range(self.data.shape[1]):
            for y in range(self.data.shape[2]):
                if self.data[layerNum, x, y] >= fadeAmount:
                    self.data[layerNum, x, y] -= fadeAmount  # fade center cell
                else:
                    self.data[layerNum, x, y] = 0