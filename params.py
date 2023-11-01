from dataclasses import dataclass
from enum import IntEnum
import os
from time import time
import re

'''
    To add a new parameter:
    1. Add a member to class Params in params.py
    2. Add a member and its default value to _privParams in ParamManager.setDefault()
       in params.py.
    3. Add an else clause to ParamManager._ingestParameter() in params.py.
    4. Add a line to the user's parameter file (default name biosim4.ini)
'''

class RunMode(IntEnum):
    STOP = 0
    RUN = 1
    PAUSE = 2
    ABORT = 3

runMode = RunMode.STOP

'''
    A private copy of Params is initialized by ParamManager.__init__(), then modified by
    UI events by ParamManager.uiMonitor(). The main simulator thread can get an
    updated, read-only, stable snapshot of Params with ParamManager.paramsSnapshot.
'''

@dataclass
class Params:
    # Initialize parameters and their default values
    population: int = 0 # >= 0
    stepsPerGeneration: int = 0 # > 0
    maxGenerations: int = 0 # >= 0
    numThreads: int = 0 # > 0
    signalLayers: int = 0 # >= 0
    genomeMaxLength: int = 0 # > 0
    maxNumberNeurons: int = 0 # > 0
    pointMutationRate: float = 0.0 # 0.0..1.0
    geneInsertionDeletionRate: float = 0.0 # 0.0..1.0
    deletionRatio: float = 0.0 # 0.0..1.0
    killEnable: bool = False # interesting
    sexualReproduction: bool = False # interesting
    chooseParentsByFitness: bool = False # interesting
    populationSensorRadius: float = 0.0 # > 0.0
    signalSensorRadius: int = 0 # > 0
    responsiveness: float = 0.0 # >= 0.0
    responsivenessCurveKFactor: int = 1 # 1, 2, 3, or 4
    longProbeDistance: int = 0 # > 0
    shortProbeBarrierDistance: int = 0 # > 0
    valenceSaturationMag: float = 0.0 #
    saveVideo: bool = False
    videoStride: int = 30 # > 0
    videoSaveFirstFrames: int = 0 # >= 0, overrides videoStride
    displayScale: int = 0
    agentSize: int = 0
    genomeAnalysisStride: int = 0 # > 0
    displaySampleGenomes: int = 0 # >= 0
    genomeComparisonMethod: int = 0 # 0 = Jaro-Winkler 1 = Hamming
    updateGraphLog: bool = False
    updateGraphLogStride: int = 0 # > 0
    challenge: int = 0
    barrierType: int = 0 # >= 0
    deterministic: bool = False
    RNGSeed: int = 0 # >= 0

    # These must not change after initialization
    sizeX: int = 2 # 2..0x10000
    sizeY: int = 2 # 2..0x10000
    genomeInitialLengthMin: int = 0 # > 0 and < genomeInitialLengthMax
    genomeInitialLengthMax: int = 0 # > 0 and < genomeInitialLengthMin
    logDir: str = ''
    imageDir: str = ''
    graphLogUpdateCommand: str = ''
    
    # These are updated automatically and not set via the parameter file
    parameterChangeGenerationNumber: int = 0  # the most recent generation number that an automatic parameter change occurred at

class ParamManager:
    def __init__(self):
        self._privParams = Params()
        self._configFilename = ''
        self._lastModTime: time = 0

    def getParamRef(self):
        return self._privParams

    def setDefaults(self):
        self._privParams.sizeX = 128
        self._privParams.sizeY = 128
        self._privParams.challenge = 6

        self._privParams.genomeInitialLengthMin = 24
        self._privParams.genomeInitialLengthMax = 24
        self._privParams.genomeMaxLength = 300
        self._privParams.logDir = "./logs/"
        self._privParams.imageDir = "./images/"
        self._privParams.population = 3000
        self._privParams.stepsPerGeneration = 300
        self._privParams.maxGenerations = 200000
        self._privParams.barrierType = 0
        self._privParams.numThreads = 4
        self._privParams.signalLayers = 1
        self._privParams.maxNumberNeurons = 5
        self._privParams.pointMutationRate = 0.001
        self._privParams.geneInsertionDeletionRate = 0.0
        self._privParams.deletionRatio = 0.5
        self._privParams.killEnable = False
        self._privParams.sexualReproduction = True
        self._privParams.chooseParentsByFitness = True
        self._privParams.populationSensorRadius = 2.5
        self._privParams.signalSensorRadius = 2.0
        self._privParams.responsiveness = 0.5
        self._privParams.responsivenessCurveKFactor = 2
        self._privParams.longProbeDistance = 16
        self._privParams.shortProbeBarrierDistance = 4
        self._privParams.valenceSaturationMag = 0.5
        self._privParams.saveVideo = True
        self._privParams.videoStride = 25
        self._privParams.videoSaveFirstFrames = 2
        self._privParams.displayScale = 8
        self._privParams.agentSize = 4
        self._privParams.genomeAnalysisStride = self._privParams.videoStride
        self._privParams.displaySampleGenomes = 5
        self._privParams.genomeComparisonMethod = 1
        self._privParams.updateGraphLog = True
        self._privParams.updateGraphLogStride = self._privParams.videoStride
        self._privParams.deterministic = False
        self._privParams.RNGSeed = 12345678
        self._privParams.graphLogUpdateCommand = "/usr/bin/gnuplot --persist ./tools/graphlog.gp" # ?
        self._privParams.parameterChangeGenerationNumber = 0

    def registerConfigFile(self, filename: str):
        self._configFilename = str(filename)

    def updateFromConfigFile(self, generationNumber):
        '''
        "generationNumber" is unsigned
        '''
        try:
            with open(self.configFilename, 'r') as cFile:
                for line in cFile:
                    line = re.sub(r'\s', '', line)
                    if line.startswith('#') or not line:
                        continue
                    name, value0 = line.split("=", 1)

                    # Process the generation specifier if present:
                    if "@" in name:
                        generationSpecifier = name.split("@")[1]
                        isUint = self.checkIfUint(generationSpecifier)
                        if not isUint:
                            print(f"Invalid generation specifier: {name}.")
                            continue
                        activeFromGeneration = int(generationSpecifier)
                        if activeFromGeneration > generationNumber:
                            continue  # This parameter value is not active yet
                        elif activeFromGeneration == generationNumber:
                            # Parameter value became active at exactly this generation number
                            self._privParams.parameterChangeGenerationNumber = generationNumber
                        name = name.split("@")[0]

                    name = name.lower()
                    value = value0.split("#")[0]
                    rawValue = value
                    value = re.sub(r'\s', '', value)
                    self._ingestParameter(name, value)

        except IOError:
            print(f"Couldn't open config file {self.configFilename}.")

    def checkParameters(self):
        if self._privParams.deterministic and self._privParams.numThreads != 1:
            print("Warning: When deterministic is true, you probably want to set numThreads = 1.")

    def _ingestParameter(self, name: str, val: str):
        name = name.lower()

        isUint = checkIfUint(val)
        uVal = int(val) if isUint else 0

        isFloat = checkIfFloat(val)
        dVal = float(val) if isFloat else 0.0

        isBool = checkIfBool(val)
        bVal = getBoolVal(val)

        while True:
            if name == "sizex" and isUint and 2 <= uVal <= 0xFFFF:
                self._privParams.size_x = uVal
                break
            elif name == "sizey" and uVal and 2 <= uVal <= 0xFFFF:
                self._privParams.size_y = uVal
                break
            elif name == "challenge" and isUint and uVal < 0xFFFF:
                self._privParams.challenge = uVal
                break
            elif name == "genomeinitiallengthmin" and isUint and 0 < uVal < 0xFFFF:
                self._privParams.genomeInitialLengthMin = uVal
                break
            elif name == "genomeinitiallengthmax" and isUint and 0 < uVal < 0xFFFF:
                self._privParams.genomeInitialLengthMax = uVal
                break
            elif name == "logdir":
                self._privParams.logDir = val
                break
            elif name == "imagedir":
                self._privParams.imageDir = val
                break
            elif name == "population" and isUint and 0 < uVal < 0xFFFFFFFF:
                self._privParams.population = uVal
                break
            elif name == "stepspergeneration" and isUint and 0 < uVal < 0xFFFF:
                self._privParams.stepsPerGeneration = uVal
                break
            elif name == "maxgenerations" and isUint and 0 < uVal < 0x7fffffff:
                self._privParams.maxGenerations = uVal
                break
            elif name == "barriertype" and isUint and uVal < 0xFFFFFFFF:
                self._privParams.barrierType = uVal
                break
            elif name == "numthreads" and isUint and uVal > 0 and uVal < 0xFFFF:
                self._privParams.numThreads = uVal
                break
            elif name == "signallayers" and isUint and uVal < 0xFFFF:
                self._privParams.signalLayers = uVal
                break
            elif name == "genomemaxlength" and isUint and 0 < uVal < 0xFFFF:
                self._privParams.genomeMaxLength = uVal
                break
            elif name == "maxnumberneurons" and isUint and 0 < uVal < 0xFFFF:
                self._privParams.maxNumberNeurons = uVal
            elif name == "pointmutationrate" and isFloat and 0.0 <= dVal <= 1.0:
                self._privParams.pointMutationRate = dVal
                break            
            elif name == "geneinsertiondeletionrate" and isFloat and 0.0 <= dVal <= 1.0:
                self._privParams.geneInsertionDeletionRate = dVal
                break            
            elif name == "deletionratio" and isFloat and 0.0 <= dVal <= 1.0:
                self._privParams.deletionRatio = dVal
                break            
            elif name == "killenable" and isBool:
                self._privParams.killEnable = bVal
                break            
            elif name == "sexualreproduction" and isBool:
                self._privParams.sexualReproduction = bVal
                break            
            elif name == "chooseparentsbyfitness" and isBool:
                self._privParams.chooseParentsByFitness = bVal
                break            
            elif name == "populationsensorradius" and isFloat and dVal > 0.0:
                self._privParams.populationSensorRadius = dVal
                break            
            elif name == "signalsensorradius" and isFloat and dVal > 0.0:
                self._privParams.signalSensorRadius = dVal
                break            
            elif name == "responsiveness" and isFloat and dVal >= 0.0:
                self._privParams.responsiveness = dVal
                break            
            elif name == "responsivenesscurvekfactor" and isUint and 1 <= uVal <= 20:
                self._privParams.responsivenessCurveKFactor = uVal
                break            
            elif name == "longprobedistance" and isUint and uVal > 0:
                self._privParams.longProbeDistance = uVal
                break            
            elif name == "shortprobebarrierdistance" and isUint and uVal > 0:
                self._privParams.shortProbeBarrierDistance = uVal
                break            
            elif name == "valencesaturationmag" and isFloat and dVal >= 0.0:
                self._privParams.valenceSaturationMag = dVal
                break            
            elif name == "savevideo" and isBool:
                self._privParams.saveVideo = bVal
                break            
            elif name == "videostride" and isUint and uVal > 0:
                self._privParams.videoStride = uVal
                break            
            elif name == "videosavefirstframes" and isUint:
                self._privParams.videoSaveFirstFrames = uVal
                break            
            elif name == "displayscale" and isUint and uVal > 0:
                self._privParams.displayScale = uVal
                break            
            elif name == "agentsize" and isFloat and dVal > 0.0:
                self._privParams.agentSize = dVal
                break            
            elif name == "genomeanalysisstride" and isUint and uVal > 0:
                self._privParams.genomeAnalysisStride = uVal
                break            
            elif name == "genomeanalysisstride" and val == "videoStride":
                self._privParams.genomeAnalysisStride = self._privParams.videoStride
                break
            elif name == "displaysamplegenomes" and isUint:
                self._privParams.displaySampleGenomes = uVal
                break            
            elif name == "genomecomparisonmethod" and isUint:
                self._privParams.genomeComparisonMethod = uVal
                break            
            elif name == "updategraphlog" and isBool:
                self._privParams.updateGraphLog = bVal
                break            
            elif name == "updategraphlogstride" and isUint and uVal > 0:
                self._privParams.updateGraphLogStride = uVal
                break            
            elif name == "updategraphlogstride" and val == "videoStride":
                self._privParams.updateGraphLogStride = self._privParams.videoStride
                break
            elif name == "deterministic" and isBool:
                self._privParams.deterministic = bVal
                break
            elif name == "rngseed" and isUint:
                self._privParams.RNGSeed = uVal
                break
            else:
                print(f"Invalid param: {name} = {val}")
                break
   

def params_init(argc, argv):
    '''
    Returns a copy of params with default values overridden by the values
    in the specified config file. The filename of the config file is saved
    inside the params for future reference.
    '''
    param_manager = ParamManager()
    # Fill this in with code to set up the initial params
    return param_manager.getParamRef()

def checkIfUint(s: str):
    '''
    s >= "0"
    '''
    s = str(s) # s>="0"
    return s.isdigit()

def checkIfInt(s: str):
    try:
        int(s)
        return True
    except ValueError:
        return False

def checkIfFloat(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False

def checkIfBool(s: str):
    return s in ["0", "1", "true", "false"]

def getBoolVal(s):
    return s in ["true", "1"]