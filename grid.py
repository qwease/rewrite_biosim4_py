from typing import Callable
from params import params
from basicTypes import Coord
from math import sqrt
import threading
from utils.RNG import getRandomGenerator

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

        self._barrierLocations: [Coord] = []
        self._barrierCenters: [Coord] = []

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
        # randomUint.instance = RandomUintGenerator()
        # randomUint.instance.initialize(params=params)
        randomUint=getRandomGenerator(p=params)
        while True:
            loc.x = randomUint(0, params.sizeX - 1).value
            loc.y = randomUint(0, params.sizeY - 1).value
            if (self.isEmptyAt(loc)):
                break
        return loc

    def createBarrier(self, barrierType: int):
        '''
        This generates barrier points, which are grid locations with value
        BARRIER. A list of barrier locations is saved in private member
        self._barrierLocations and, for some scenarios, self._barrierCenters.
        Those members are available read-only with Grid::getBarrierLocations().
        This function assumes an empty grid. This is typically called by
        the main simulator thread after Grid::init() or Grid::zeroFill().

        This file typically is under constant development and change for
        specific scenarios.
        '''
        self._barrierLocations.clear()
        self._barrierCenters.clear() # used only for some barrier types
        def drawBox(minX, minY, maxX, maxY):
            for x in range(minX, maxX + 1):
                for y in range(minY, maxY + 1):
                    self.set(x, y, BARRIER)
                    self._barrierLocations.append(Coord(x,y))
        
        def randomLoc():
            randomUint=getRandomGenerator(p=params)
            return Coord(randomUint(0, params.sizeX).value, randomUint(0, params.sizeY).value)
        
        # after I have completed to translation,
        # test if the addition of the following two lines
        # is better? 
        # randomUint.instance = RandomUintGenerator()
        # randomUint.instance.initialize(params=params)

        if barrierType == 0:
            return

        elif barrierType == 1: # Vertical bar in constant location
            minX = params.sizeX // 2
            maxX = minX + 1
            minY = params.sizeY // 4
            maxY = minY + params.sizeY // 2

            for x in range(minX, maxX + 1):
                for y in range(minY, maxY + 1):
                    self.set(x, y, BARRIER)
                    self._barrierLocations.append(Coord(x,y))

        elif barrierType == 2: # Vertical bar in random location
            randomUint=getRandomGenerator(p=params)
            minX = randomUint(20, params.sizeX - 20).value
            maxX = minX + 1
            minY = randomUint(20, params.sizeY // 2 - 20).value
            maxY = minY + params.sizeY // 2

            for x in range(minX, maxX + 1):
                for y in range(minY, maxY + 1):
                    self.set(x, y, BARRIER)
                    self._barrierLocations.append(Coord(x,y))

        elif barrierType == 3: # five blocks staggered star-like
            blockSizeX = 2
            blockSizeY = params.sizeX // 3

            x0 = params.sizeX // 4 - blockSizeX // 2
            y0 = params.sizeY // 4 - blockSizeY // 2
            x1 = x0 + blockSizeX
            y1 = y0 + blockSizeY

            drawBox(x0, y0, x1, y1)
            x0 += params.sizeX // 2
            x1 = x0 + blockSizeX
            drawBox(x0, y0, x1, y1)
            y0 += params.sizeY // 2
            y1 = y0 + blockSizeY
            drawBox(x0, y0, x1, y1)
            x0 -= params.sizeX // 2
            x1 = x0 + blockSizeX
            drawBox(x0, y0, x1, y1)
            x0 = params.sizeX // 2 - blockSizeX // 2
            x1 = x0 + blockSizeX
            y0 = params.sizeY // 2 - blockSizeY // 2
            y1 = y0 + blockSizeY
            drawBox(x0, y0, x1, y1)
        
        elif barrierType == 4: # Horizontal bar in constant location
            minX = params.sizeX // 4
            maxX = minX + params.sizeX // 2
            minY = params.sizeY // 2 + params.sizeY // 4
            maxY = minY + 2
            drawBox(minX, minY, maxX, maxY)
        
        elif barrierType == 5:  # Three floating islands -- different locations every generation
            radius = 3.0
            margin = 2 * radius
            center0 = randomLoc()
            center1 = None
            center2 = None

            while True:
                center1 = randomLoc()
                if (center0 - center1).length >= margin:
                    break

            while True:
                center2 = randomLoc()
                if (center0 - center2).length >= margin and (center1 - center2).length >= margin:
                    break
            self._barrierCenters.extend([center0, center1, center2])
            
            def f(loc: Coord):
                if self.isEmptyAt(loc):
                    self.set(loc, val=BARRIER)
                self._barrierLocations.append(loc)
            
            self.visitNeighborhood(loc=center0, radius=radius, f=f)
            self.visitNeighborhood(loc=center1, radius=radius, f=f)
            self.visitNeighborhood(loc=center2, radius=radius, f=f)

        elif barrierType == 6:  # Spots, specified number, radius, locations
            numberOfLocations = 5
            radius = 5.0

            def f(loc: Coord):
                if self.isEmptyAt(loc):
                    self.set(loc, val= BARRIER)
                self._barrierLocations.append(loc)

            verticalSliceSize = params.sizeY // (numberOfLocations + 1)

            for n in range(1, numberOfLocations + 1):
                loc = Coord(params.sizeX // 2, n * verticalSliceSize)
                self.visitNeighborhood(loc, radius, f)
                self._barrierCenters.append(loc)

        else:
            raise ValueError("Invalid barrier_type")


    def getBarrierLocations(self) -> [Coord]:
        return self._barrierLocations

    def getBarrierCenters(self) -> [Coord]:
        return self._barrierCenters


    def visitNeighborhood(self, loc: Coord, radius: float, f: Callable[[Coord], None]):
        '''
        This is a utility function used when inspecting a local neighborhood around
        some location. This function feeds each valid (in-bounds) location in the specified
        neighborhood to the specified function. Locations include self (center of the neighborhood).
        '''
        for dx in range(-min(int(radius), loc.x), min(int(radius), (params.sizeX - loc.x) - 1) + 1):
            x = loc.x + dx
            if not (x >= 0 and x < params.sizeX):
                raise ValueError("Assertion failed: x >= 0 and x < params.sizeX")
            extentY = int(sqrt(radius * radius - dx * dx))
            for dy in range(-min(extentY, loc.y), min(extentY, (params.sizeY - loc.y) - 1) + 1):
                y = loc.y + dy
                if not (y >= 0 and y < params.sizeY):
                    raise ValueError("Assertion failed: y >= 0 and y < params.sizeY")
                f(Coord(x, y))


def unitTestGridVisitNeighborhood():
    ...

if __name__ == "__main__":
    # prove if an empty function could be rewrited in-file
    def geneticDiversity() -> float:  # 0.0..1.0
        return 0.3
    print(geneticDiversity())

    # multithread testing
    
    def thread_function(thread_id):
        grid=Grid()
        grid.init(params.sizeX,params.sizeY)
        loc = grid.findEmptyLocation()
        grid.createBarrier(6)
        print(grid.data)
        print(f'Thread-{thread_id} value: ', loc.x,loc.y)
    
    # The globally-scoped random number generator.
    # Each thread will have a private instance of the RNG.
    # randomUint.instance = RandomUintGenerator()
    # randomUintInst = randomUint.instance.initialize(params=params)

    threads = []

    import time
    start = time.time()
    # Create and start 10 threads
    for i in range(7):
        t = threading.Thread(target=thread_function, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
    
    end= time.time()
    print(end-start)