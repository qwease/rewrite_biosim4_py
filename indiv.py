from sys import path
import threading
from path import Path
# caution: path[0] is reserved for script path (or '' in REPL)
if str(Path(__file__).parent) not in path:
    path.append(str(Path(__file__).parent)) 
# print(path)
from basicTypes import *
from genome_neurons import *
from sensors_actions import *
from simulator import *

class Indiv:
    def __init__(self, index, loc, genome):
        self.alive = False
        self.index = index  # index into peeps[] container
        self.loc: Coord = loc  # refers to a location in grid[][]
        self.birthLoc: Coord = None
        self.age = 0
        self.genome: Genome = genome
        self.nnet: NeuralNet = NeuralNet()  # derived from .genome
        self.responsiveness: float = 0.0  # 0.0..1.0 (0 is like asleep)
        self.oscPeriod = 2  # 2..4*params.stepsPerGeneration (TBD, see executeActions())
        self.longProbeDist = 0  # distance for long forward probe for obstructions
        self.lastMoveDir: Dir = None  # direction of last movement
        self.challengeBits = 0  # modified when the indiv accomplishes some task
        self.actions = [0.0] * Action.NUM_ACTIONS

    def feedForward(self, simStep):  # reads sensors, returns actions
        '''
        return Type: array of float, length: Action::NUM_ACTIONS
        '''
        pass

    def getSensor(self, Sensor, simStep):
        pass

    def initialize(self, index_, loc_: Coord, genome_: Genome):
        self.index = index_
        self.loc = loc_
        # self.birthLoc = loc_
        grid.set(loc_, index_)  # This needs a global 'grid' object or passed as a parameter
        self.age = 0
        self.oscPeriod = 34  # ToDo !!! define a constant
        self.alive = True
        self.lastMoveDir = Dir.random8()  # This needs a Dir class with a method random8()
        self.responsiveness = 0.5  # range 0.0..1.0
        self.longProbeDist = params.longProbeDistance  # params is not defined in the given context
        self.challengeBits = False  # will be set true when some task gets accomplished
        self.genome = genome_ # one genome data in memory 
        self.createWiringFromGenome()

    def createWiringFromGenome(self):  # creates .nnet member from .genome member
        pass

    def printNeuralNet(self):
        pass

    def printIGraphEdgeList(self):
        pass

    def printGenome(self):
        pass