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
        # # Increase the neighbors, include the center
        # visitNeighborhood(loc, radius, lambda loc: self.increase(layerNum, loc, neighborIncreaseAmount))

        # # Increase the center cell
        # self.increase(layerNum, loc, centerIncreaseAmount)
        with self.lock:
            # Increase the neighbors, include the center
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

if __name__ == '__main__':
    # ----unit test below----
    import unittest
    import multiprocessing
    from multiprocessing.managers import BaseManager
    def increment(signals,loc):
                for _ in range(100):
                    signals.increment(0, loc)

    def fade(signals, layerNum):
            fadeAmount = 1

            for x in range(signals.data.shape[1]):
                for y in range(signals.data.shape[2]):
                    if signals.data[layerNum, x, y] >= fadeAmount:
                        signals.data[layerNum, x, y] -= fadeAmount  # fade center cell
                    else:
                        signals.data[layerNum, x, y] = 0 

    class MyManager(BaseManager):
        pass

    MyManager.register('Signals', Signals)

    class TestSignals(unittest.TestCase):
        def setUp(self):
            self.signals = Signals()
            self.signals.init(2, 3, 3)

        def test_init(self):
            self.assertEqual(self.signals.data.shape, (2, 3, 3))

        def test_getMagnitude(self):
            loc = Coord(1, 1)
            self.assertEqual(self.signals.getMagnitude(1, loc), 0)

        def test_increment(self):
            loc = Coord(1, 1)
            self.signals.increment(1, loc)
            self.assertEqual(self.signals.getMagnitude(1, loc), 3)
            self.assertEqual(self.signals.getMagnitude(1, Coord(1, 2)), 1)

        def test_increase(self):
            loc = Coord(1, 1)
            self.signals.increase(1, loc, 3)
            self.assertEqual(self.signals.getMagnitude(1, loc), 3)

        def test_zeroFill(self):
            self.signals.zeroFill()
            for x in range(self.signals.data.shape[1]):
                for y in range(self.signals.data.shape[2]):
                    self.assertEqual(self.signals.data[1, x, y], 0)

        def test_fade(self):
            loc = Coord(1, 1)
            self.signals.increase(1, loc, 3)
            self.signals.fade(1)
            self.assertEqual(self.signals.getMagnitude(1, loc), 2)

        def test_multiprocessing_lock(self):
            with MyManager() as manager:
                # Create Signals object on the manager
                signals = manager.Signals()
                signals.init(1, 256, 256)

                loc = Coord(1, 1)
                ps = []
                # Start two processes that increment the same location
                for _ in range(2):
                    p = multiprocessing.Process(target=increment, args=(signals, loc))
                    ps.append(p)

                for p in ps:
                    p.start()

                for p in ps:
                    p.join()

                # Check the result
                self.assertEqual(signals.getMagnitude(0, Coord(0,0)), 200)
    unittest.main()
    

