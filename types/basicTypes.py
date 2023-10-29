# encoding: utf-8

from enum import Enum, IntEnum
from typing import Union
from utils.RNG import randomUint
from math import sqrt
import ctypes
from ctypes import c_uint8, c_int16, c_int64


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
    def __init__(self, dir=Compass.CENTER):
        self._dir9 : Compass = dir

    @staticmethod
    def random8() -> 'Dir':
        return Dir(Compass.N).rotate(randomUint(0, 7))

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
        return NormalizedCoords[self.asInt]

    @property
    def asNormalizedPolar(self) -> 'Polar':
        return Polar(1, self._dir9)
    
    @property
    def rotate(self, n=0) -> 'Dir':
        return rotations[self.asInt * 8 + (n & 7)]

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
            return self.asInt == c_uint8(d)
        elif isinstance(d, Dir):
            return self.asInt == d.asInt
        else:
            raise TypeError

    def __ne__(self, d:Union[Compass,'Dir']):
        if isinstance(d, Compass):
            return self.asInt != c_uint8(d)
        elif isinstance(d, Dir):
            return self.asInt != d.asInt
        else:
            raise TypeError

class Coord:
    def __init__(self, x=0, y=0):
        # c_int16?
        self.x = x
        self.y = y

    @property
    def isNormalized(self) -> bool:
        return -1 <= self.x <= 1 and -1 <= self.y <= 1

    @property
    def normalize(self) -> 'Coord':
        # Implement this method
        return self.asDir.asNormalizedCoord
    
    @property
    def length(self):
        return int(sqrt(self.x * self.x + self.y * self.y)) # round down

    @property
    def asDir(self) -> Dir:
        tanN = 13860
        tanD = 33461
        conversion : [Dir]= [S, C, SW, N, SE, E, N,
                       N, N, N, W, NW, N, NE, N, N]

        #make sure elements in conversion list is of type Dir
        for i in conversion:
            i=Dir(i)
        
        xp = self.x * tanD + self.y * tanN
        yp = self.y * tanD - self.x * tanN

        return conversion[(yp > 0) * 8 + (xp > 0) * 4 + (yp > xp) * 2 + (yp >= -xp)]
    
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

    def raySameness(self, other:Union['Coord',Dir]):
        if isinstance(other, Coord):
            # returns -1.0 (opposite) .. 1.0 (same)
            mag = (self.x * self.x + self.y * self.y) * (other.x * other.x + other.y * other.y)
            if mag == 0:
                return 1.0  # anything is "same" as zero vector

            return (self.x * other.x + self.y * other.y) / sqrt(mag)
        elif isinstance(other, Dir):
            # returns -1.0 (opposite) .. 1.0 (same)
            return self.raySameness(other.asNormalizedCoord)

class Polar:
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

        len = coordMags[self.dir.asInt()] * self.mag

        temp = ((self.mag >> 32) ^ ((1 << 31) - 1))
        len = (len + temp) // (1 << 32)  # Integer division

        return NormalizedCoords[self.dir.asInt()] * len

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

#    Coord { (d%3) - 1, (trunc)(d/3) - 1  }

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
    pass