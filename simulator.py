# encoding: utf-8

from sys import path
from path import Path
# caution: path[0] is reserved for script path (or '' in REPL)
if str(Path(__file__).parent) not in path:
    path.append(str(Path(__file__).parent)) 
# print(path)
from params import params
from grid import Grid
from utils.RNG import getRandomGenerator
from sensors_actions import printSensorsActions
from signals import Signals

printSensorsActions()

# -----
# init param variable like C++,
# already initialised in params.py by initParams()
# -----

randomUint=getRandomGenerator(p=params)

grid = Grid()
signals = Signals()
# peeps = Peeps()
grid.init(sizeX=params.sizeX,sizeY=params.sizeY)
signals.init(numLayers=params.signalLayers, sizeX=params.sizeX, sizeY=params.sizeY)




# params = params

# randomUint.instance=RandomUintGenerator()
# randomUint.instance.initialize(params=params) # now you can treat randomUint.instance as an object


# Check the following link to see ideas of how to implement main while loop
# https://poe.com/s/VcbEhblIMAROzkEo1Xq9 