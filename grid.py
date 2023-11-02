from typing import Callable
from simulator import *
from basicTypes import *

import numpy as np
# import torch
# import cupy as cp

# Grid is a somewhat dumb 2D container of unsigned 16-bit values.
# Grid understands that the elements are either EMPTY, BARRIER, or
# otherwise an index value into the peeps container.
# The elements are allocated and cleared to EMPTY in the ctor.
# Prefer .at() and .set() for random element access. Or use Grid[x][y]
# for direct access where the y index is the inner loop.
# Element values are not otherwise interpreted by class Grid.

EMPTY = 0  # Index value 0 is reserved
BARRIER = 0xffff

class Grid:
    '''
    Column order here allows us to access grid elements as data[x][y]
    while thinking of x as column and y as row
    '''
    def __init__(self):
        # numpy
        # import numpy as np
        self.data = np.array([]) # represents the Column struct in C++
        
        # cupy
        # import cupy as cp
        # self.data = cp.array([])

        # pytorch
        # self.data = torch.tensor([])

        self.barrierLocations: [Coord] = []
        self.barrierCenters: [Coord] = []

    def init(self, sizeX: int, sizeY: int):
        # numPy
        self.data = np.zeros((sizeX, sizeY), dtype=np.uint16)

        # cupy
        # self.data = cp.zeros((sizeX, sizeY), dtype=cp.uint16)

        # pytorch
        # self.data = torch.zeros((sizeX, sizeY), dtype=torch.int32)
        # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # print(device)
        # self.data.to(device)

    def zeroFill(self):
        self.data.fill(0)

    @property
    def sizeX(self):
        return self.data.shape[0]

    @property
    def sizeY(self):
        return self.data.shape[1]

    def isInBounds(self, loc: Coord):
        return 0 <= loc.x < self.sizeX and 0 <= loc.y < self.sizeY

    def isEmptyAt(self, loc: Coord):
        return self.at(loc) == EMPTY

    def isBarrierAt(self, loc: Coord):
        return self.at(loc) == BARRIER

    def isOccupiedAt(self, loc: Coord):
        return self.at(loc) != EMPTY and self.at(loc) != BARRIER

    def isBorder(self, loc: Coord):
        return loc.x == 0 or loc.x == self.sizeX - 1 or loc.y == 0 or loc.y == self.sizeY - 1

    def at(self, x, y=None):
        if isinstance(x, Coord):
            return self.data[x.x][x.y]
        else:
            # then we assume x, y are of type uint16_t
            return self.data[x][y]

        # original C++ code:
        # uint16_t at(Coord loc) const { return data[loc.x][loc.y]; }
        # uint16_t at(uint16_t x, uint16_t y) const { return data[x][y]; }

        # Alternative 1:
        # def at(self, *args):
        #     if len(args) == 1:
        #         loc = args[0]
        #         return self.data[loc.x][loc.y]
        #     elif len(args) == 2:
        #         x, y = args
        #         return self.data[x][y]
        
        # Alternative 2:
        # def at(self, x, y=None):
        #     if isinstance(x, Coord):
        #         return self.data[x.x][x.y]
        #     else:
        #         return self.data[x][y]

    def set(self, x, y=None, val = -1):
        '''
        val >= 0
        '''
        if val >=0 :
            if isinstance(x, Coord):
                self.data[x.x][x.y] = val
            else:
                # then we assume x, y are of type uint16_t
                self.data[x][y] = val            

        # original C++ code:
        # void set(Coord loc, uint16_t val) { data[loc.x][loc.y] = val; }
        # void set(uint16_t x, uint16_t y, uint16_t val) { data[x][y] = val; }

    def findEmptyLocation(self) -> Coord:
        loc = Coord()

        while True:
            randomUint.instance = RandomUintGenerator()
            randomUint.instance.initialize(params=params)
            loc.x = randomUint.instance(0, params.sizeX - 1).value
            loc.y = randomUint.instance(0, params.sizeY - 1).value
            if (grid.isEmptyAt(loc)):
                break
        return loc

    def createBarrier(self, barrierType: int):
        ...

    def getBarrierLocations(self) -> [Coord]:
        return self.barrierLocations

    def getBarrierCenters(self) -> [Coord]:
        return self.barrierCenters


def visitNeighborhood(loc: Coord, radius: float, f: Callable[[Coord], None]):
    ...


def unitTestGridVisitNeighborhood():
    ...

if __name__ == "__main__":
    # prove if an empty function could be rewrited in-file
    def geneticDiversity() -> float:  # 0.0..1.0
        return 0.3
    print(geneticDiversity())

    # multithread testing
    grid=Grid()
    def thread_function(thread_id):
        grid.init(10000,10000)
        loc = grid.findEmptyLocation()
        print(f'Thread-{thread_id} value: ', loc.x,loc.y)
    
    # The globally-scoped random number generator.
    # Each thread will have a private instance of the RNG.
    # randomUint.instance = RandomUintGenerator()
    # randomUintInst = randomUint.instance.initialize(params=params)

    threads = []

    import time
    start = time.time()
    # Create and start 10 threads
    for i in range(10):
        t = threading.Thread(target=thread_function, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
    
    end= time.time()
    print(end-start)