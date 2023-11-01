# encoding: utf-8

from sys import path
from path import Path
# caution: path[0] is reserved for script path (or '' in REPL)
path.append(str(Path(__file__).parent))
# print(path)
from params import ParamManager
from grid import Grid

grid= Grid()
paramManager = ParamManager()
params = paramManager.getParamRef()