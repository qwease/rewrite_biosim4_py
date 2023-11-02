# encoding: utf-8

from sys import path
from path import Path
# caution: path[0] is reserved for script path (or '' in REPL)
if str(Path(__file__).parent) not in path:
    path.append(str(Path(__file__).parent)) 
# print(path)
from params import ParamManager
from grid import Grid
from utils.RNG import randomUint,RandomUintGenerator

grid= Grid()
paramManager = ParamManager()
params = paramManager.getParamRef()
randomUint.instance=RandomUintGenerator()
randomUint.instance.initialize(params=params) # now you can treat randomUint.instance as an object