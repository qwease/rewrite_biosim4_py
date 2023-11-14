# encoding: utf-8

from sys import path
from path import Path
# caution: path[0] is reserved for script path (or '' in REPL)
if str(Path(__file__).parent) not in path:
    path.append(str(Path(__file__).parent)) 
# print(path)
from params import params,paramManager
from grid import Grid
from utils.RNG import getRandomGenerator

grid = Grid()
randomUint=getRandomGenerator(p=params)

# params = params

# randomUint.instance=RandomUintGenerator()
# randomUint.instance.initialize(params=params) # now you can treat randomUint.instance as an object


# Check the following link to see ideas of how to implement main while loop
# https://poe.com/s/VcbEhblIMAROzkEo1Xq9 