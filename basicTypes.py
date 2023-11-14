# encoding: utf-8
from sys import path
from path import Path
if str(Path(__file__).parent.parent) not in path:
    path.append(str(Path(__file__).parent.parent))
import threading

# caution: path[0] is reserved for script path (or '' in REPL)

# print(sys.path)

from params import params
from enum import Enum, IntEnum
from typing import Union
from utils.RNG import getRandomGenerator
from math import sqrt
from ctypes import c_uint8, c_int16, c_int64, c_uint32

'''
Basic types used throughout the project:

Compass - an enum with enumerants SW, S, SE, W, CENTER, E, NW, N, NE

    Compass arithmetic values:

        6  7  8
        3  4  5
        0  1  2

Dir, Coord, Polar, and their constructors:
    ctor (Constructor)
    Dir - abstract type for 8 directions plus center
    ctor Dir(Compass = CENTER)

    Coord - signed int16_t pair, absolute location or difference of locations
    ctor Coord() = 0,0

    Polar - signed magnitude and direction
    ctor Polar(Coord = 0,0)

Conversions

    uint8_t = Dir.asInt()

    Dir = Coord.asDir()
    Dir = Polar.asDir()

    Coord = Dir.asNormalizedCoord()
    Coord = Polar.asCoord()

    Polar = Dir.asNormalizedPolar()
    Polar = Coord.asPolar()

Arithmetic

    Dir.rotate(int n = 0)

    Coord = Coord + Dir
    Coord = Coord + Coord
    Coord = Coord + Polar

    Polar = Polar + Coord (additive)
    Polar = Polar + Polar (additive)
    Polar = Polar * Polar (dot product)
'''

randomUintLocalThread = threading.local()

class Compass(IntEnum):
    SW = 0
    S = 1
    SE = 2
    W = 3
    CENTER = 4
    E = 5
    NW = 6
    N = 7
    NE = 8

class Dir:
    '''
    Supports the eight directions in enum class Compass plus CENTER.
    '''
    def __init__(self, dir=Compass.CENTER):
        self._dir9 : Compass = dir

    @staticmethod
    def random8() -> 'Dir':
        #--------may be call in other threads
        randomUint = getRandomGenerator(p=params)
        #--------
        return Dir(Compass.N).rotate(randomUint(min=c_uint32(0), max=c_uint32(7)).value)

    def assign(self, d: Compass) -> 'Dir':
        # equivalent for operator=() in C++
        # d is a constant
        self._dir9 = d
        return self

    @property
    def asInt(self) -> c_uint8:
        return c_uint8(self._dir9)

    @property
    def asNormalizedCoord(self) -> 'Coord':
        # (-1, -0, 1, -1, 0, 1)
        return NormalizedCoords[self.asInt.value]

    @property
    def asNormalizedPolar(self) -> 'Polar':
        return Polar(1, self._dir9)
    
    def rotate(self, n=0) -> 'Dir':
        return Dir(rotations[self.asInt.value * 8 + (n & 7)])

    @property
    def rotate90DegCW(self) -> 'Dir':
        # CW: Clockwise
        return self.rotate(2)

    @property
    def rotate90DegCCW(self) -> 'Dir':
        # CCW: Conter-Clockwise
        return self.rotate(-2)

    @property
    def rotate180Deg(self) -> 'Dir':
        return self.rotate(4)
    
    #operator overload
    def __eq__(self, d:Union[Compass,'Dir']):
        if isinstance(d, Compass):
            return self.asInt.value == c_uint8(d)
        elif isinstance(d, Dir):
            return self.asInt.value == d.asInt.value
        else:
            raise TypeError

    def __ne__(self, d:Union[Compass,'Dir']):
        if isinstance(d, Compass):
            return self.asInt.value != c_uint8(d).value
        elif isinstance(d, Dir):
            return self.asInt.value != d.asInt.value
        else:
            raise TypeError

class Coord:
    '''
    Coordinates range anywhere in the range of int (int16_t). Coordinate arithmetic
    wraps like int (int16_t). Can be used, e.g., for a location in the simulator grid, or
    for the difference between two locations.
    '''
    def __init__(self, x=0, y=0):
        # c_int16?
        self.x = x
        self.y = y

    @property
    def isNormalized(self) -> bool:
        return -1 <= self.x <= 1 and -1 <= self.y <= 1

    @property
    def normalize(self) -> 'Coord':
        '''
        A normalized Coord has x and y == -1, 0, or 1.
        A normalized Coord may be used as an offset to one of the
        8-neighbors.
        We'll convert the Coord into a Dir, then convert Dir to normalized Coord.
        '''
        return self.asDir.asNormalizedCoord
    
    @property
    def length(self):
        return int(sqrt(self.x * self.x + self.y * self.y)) # round down

    @property
    def asDir(self) -> Dir:
        '''
        Effectively, we want to check if a coordinate lies in a 45 degree region (22.5 degrees each side)
        centered on each compass direction. By first rotating the system by 22.5 degrees clockwise
        the boundaries to these regions become much easier to work with as they just align with the 8 axes.
        (Thanks to @Asa-Hopkins for this optimization -- drm)

        tanN/tanD is the best rational approximation to tan(22.5) under the constraint that
        tanN + tanD < 2**16 (to avoid overflows). We don't care about the scale of the result,
        only the ratio of the terms. The actual rotation is (22.5 - 1.5e-8) degrees, whilst
        the closest a pair of ints come to any of these lines is 8e-8 degrees, so the result is exact.
        '''
        tanN = 13860
        tanD = 33461
        conversion : [Dir]= [S, C, SW, N, SE, E, N,
                       N, N, N, W, NW, N, NE, N, N]

        # make sure elements in conversion list is of type Dir
        # for i in conversion:
        #     i=Dir(i)
        
        xp = self.x * tanD + self.y * tanN
        yp = self.y * tanD - self.x * tanN

        # We can easily check which side of the four boundary lines
        # the point now falls on, giving 16 cases, though only 9 are
        # possible.
        return Dir(conversion[(yp > 0) * 8 + (xp > 0) * 4 + (yp > xp) * 2 + (yp >= -xp)])
    
    @property
    def asPolar(self) -> 'Polar':
         return Polar(int(self.length), self.asDir)

    def __eq__(self, other) -> bool:
        if isinstance(other, Coord):
            return self.x == other.x and self.y == other.y
        else:
            raise TypeError

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __add__(self, other) -> 'Coord':
        if isinstance(other, Coord):
            return Coord(self.x + other.x, self.y + other.y)
        elif isinstance(other, Dir):
            return self + other.asNormalizedCoord

    def __sub__(self, other):
        if isinstance(other, Coord):
            return Coord(self.x - other.x, self.y - other.y)
        elif isinstance(other, Dir):
            return self - other.asNormalizedCoord

    def __mul__(self, other):
        if isinstance(other, int):
            return Coord(self.x * other, self.y * other)
        else:
            raise TypeError

    def raySameness(self, other:Union['Coord',Dir]) -> float:
        '''
        Coord:
        returns -1.0 (opposite directions) .. +1.0 (same direction)
        returns 1.0 if either vector is (0,0)

        Dir:
        returns -1.0 (opposite directions) .. +1.0 (same direction)
        returns 1.0 if self is (0,0) or d is CENTER
        '''
        if isinstance(other, Coord):
            # returns -1.0 (opposite) .. 1.0 (same)
            mag = (self.x * self.x + self.y * self.y) * (other.x * other.x + other.y * other.y)
            if mag == 0:
                return 1.0  # anything is "same" as zero vector

            return (self.x * other.x + self.y * other.y) / sqrt(mag)
        elif isinstance(other, Dir):
            # returns -1.0 (opposite) .. 1.0 (same)
            return self.raySameness(other.asNormalizedCoord)
        else:
            raise TypeError


class Polar:
    '''
    Polar magnitudes are signed integers so that they can extend across any 2D
    area defined by the Coord class.
    '''
    def __init__(self, mag0=0, dir0: Compass =Compass.CENTER):
        self.mag = mag0
        if isinstance(dir0, Compass):
            self.dir = Dir(dir0)
        elif isinstance(dir0, Dir):
            self.dir = dir0
        else:
            raise TypeError

    @property
    def asCoord(self) -> Coord:
        '''
        (Thanks to @Asa-Hopkins for this optimized function -- drm)

        3037000500 is 1/sqrt(2) in 32.32 fixed point
        '''
        # no c_int64 needed?
        coordMags = [
            3037000500,  # SW
            1 << 32,     # S
            3037000500,  # SE
            1 << 32,     # W
            0,           # CENTER
            1 << 32,     # E
            3037000500,  # NW
            1 << 32,     # N
            3037000500   # NE
        ]

        len = coordMags[self.dir.asInt.value] * self.mag

        # We need correct rounding, the idea here is to add/sub 1/2 (in fixed point)
        # and truncate. We extend the sign of the magnitude with a cast,
        # then shift those bits into the lower half, giving 0 for mag >= 0 and
        # -1 for mag<0. An XOR with this copies the sign onto 1/2, to be exact
        # we'd then also subtract it, but we don't need to be that precise.
        temp = ((self.mag >> 32) ^ ((1 << 31) - 1))
        len = (len + temp) // (1 << 32)  # Integer division

        return NormalizedCoords[self.dir.asInt.value] * len

# This rotates a Dir value by the specified number of steps. There are
# eight steps per full rotation. Positive values are clockwise; negative
# values are counterclockwise. E.g., rotate(4) returns a direction 90
# degrees to the right.
NW = Compass.NW
N = Compass.N
NE = Compass.NE
E = Compass.E
SE = Compass.SE
S = Compass.S
SW = Compass.SW
W = Compass.W
C = Compass.CENTER

rotations:[Dir] = [SW, W, NW, N, NE, E, SE, S,
                            S, SW, W, NW, N, NE, E, SE,
                            SE, S, SW, W, NW, N, NE, E,
                            W, NW, N, NE, E, SE, S, SW,
                            C, C, C, C, C, C, C, C,
                            E, SE, S, SW, W, NW, N, NE,
                            NW, N, NE, E, SE, S, SW, W,
                            N, NE, E, SE, S, SW, W, NW,
                            NE, E, SE, S, SW, W, NW, N]

# A normalized Coord is a Coord with x and y == -1, 0, or 1.
# A normalized Coord may be used as an offset to one of the
# 8-neighbors.

# A Dir value maps to a normalized Coord using

#    Coord ( (d%3) - 1, (trunc)(d/3) - 1  )

#    0 => -1, -1  SW
#    1 =>  0, -1  S
#    2 =>  1, -1, SE
#    3 => -1,  0  W
#    4 =>  0,  0  CENTER
#    5 =>  1   0  E
#    6 => -1,  1  NW
#    7 =>  0,  1  N
#    8 =>  1,  1  NE
NormalizedCoords : [Coord] = [ 
    Coord(-1,-1), # SW
    Coord(0,-1),  # S
    Coord(1,-1),  # SE
    Coord(-1,0),  # W
    Coord(0,0),   # CENTER
    Coord(1,0),   # E
    Coord(-1,1),  # NW
    Coord(0,1),   # N
    Coord(1,1)    # NE
]

if __name__ == "__main__":
    def test_dir():
        # pass
        def thread_function(thread_id):
            d1= Dir(Compass.CENTER)
            print(f'Thread-{thread_id} value: ', d1.random8().asInt)
        
        # d2= Dir(Compass.E)
        # d1.asInt.value
        # d1.asNormalizedCoord
        # d1.asNormalizedPolar
        # d1.rotate(3)

        threads=[]
        for i in range(10):
            t = threading.Thread(target=thread_function, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()
    
        # d1.rotate180Deg
        # d1.rotate90DegCCW
        # d1.rotate90DegCCW
        # d1.rotate90DegCW

        # print(d1.asInt.value)
        # d1.assign(Compass.E)
        # print(d1==Compass.E,d2!=Compass.N,d2==Dir(),d2!=Dir())

    def test_coord():
        # pass
        c1=Coord(223,-1235442632474573473354)
        c1.asDir
        c1.asPolar
        c1.isNormalized
        c1.normalize
        c1.isNormalized
        c1.length
        d1=Dir(Compass.SW)
        c1.raySameness(d1)
        c2=Coord(-4253461,-1235442632474573473354)
        c2.asDir
        c2.asPolar
        c2.isNormalized
        c2.normalize
        c2.isNormalized
        c2.length
        c2.raySameness(c1)

        c1==c2
        c1!=c2

        c1+c2
        c1-c2
        c1*0
        c2-(-7)

    def test_polar():
        # pass
        d1=Dir(Compass.SE)
        p1 = Polar(2147483647,Compass.NE)
        p1.asCoord
        p1.dir
        p1.mag
        p2=Polar(mag0=0,dir0=d1)
        p2.asCoord
        p2.dir
        p2.mag

    test_dir()
    test_coord()
    test_polar()