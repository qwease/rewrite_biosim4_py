# encoding: utf-8

# This file defines which sensor input neurons and which action output neurons
# are compiled into the simulator. This file can be modified to create a simulator
# executable that supports only a subset of all possible sensor or action neurons.

# Neuron Sources (Sensors) and Sinks (Actions)

from enum import Enum, auto
# These sensor, neuron, and action value ranges are here for documentation
# purposes. Most functions now assume these ranges. We no longer support changes
# to these ranges.
SENSOR_MIN : float= 0.0
SENSOR_MAX : float= 1.0
SENSOR_RANGE : float= SENSOR_MAX - SENSOR_MIN

NEURON_MIN : float= -1.0
NEURON_MAX : float= 1.0
NEURON_RANGE : float= NEURON_MAX - NEURON_MIN

ACTION_MIN : float= 0.0
ACTION_MAX : float= 1.0
ACTION_RANGE : float= ACTION_MAX - ACTION_MIN


# Place the sensor neuron you want enabled prior to NUM_SENSES. Any
# that are after NUM_SENSES will be disabled in the simulator.
# If new items are added to this enum, also update the name functions
# in analysis.py.

# I means data about the individual, mainly stored in (Indiv)
# W means data about the environment, mainly store in (Peeps or Grid)
class Sensor(Enum):
    LOC_X= auto()           # I distance from left edge
    LOC_Y= auto()           # I distance from bottom
    BOUNDARY_DIST_X= auto() # I X distance to nearest edge of world
    BOUNDARY_DIST= auto()   # I distance to nearest edge of world
    BOUNDARY_DIST_Y= auto() # I Y distance to nearest edge of world
    GENETIC_SIM_FWD= auto() # I genetic similarity forward
    LAST_MOVE_DIR_X= auto() # I +- amount of X movement in last movement
    LAST_MOVE_DIR_Y= auto() # I +- amount of Y movement in last movement
    LONGPROBE_POP_FWD= auto() # W long look for population forward
    LONGPROBE_BAR_FWD= auto() # W long look for barriers forward
    POPULATION= auto()      # W population density in neighborhood
    POPULATION_FWD= auto()  # W population density in the forward-reverse axis
    POPULATION_LR= auto()   # W population density in the left-right axis
    OSC1= auto()            # I oscillator +-value
    AGE= auto()             # I
    BARRIER_FWD= auto()     # W neighborhood barrier distance forward-reverse axis
    BARRIER_LR= auto()      # W neighborhood barrier distance left-right axis
    RANDOM= auto()          #   random sensor value, uniform distribution
    SIGNAL0= auto()         # W strength of signal0 in neighborhood
    SIGNAL0_FWD= auto()     # W strength of signal0 in the forward-reverse axis
    SIGNAL0_LR= auto()      # W strength of signal0 in the left-right axis
    NUM_SENSES= auto()      # <<------------------ END OF ACTIVE SENSES MARKER


# Place the action neuron you want enabled prior to NUM_ACTIONS. Any
# that are after NUM_ACTIONS will be disabled in the simulator.
# If new items are added to this enum, also update the name functions
# in analysis.py.
# I means the action affects the individual internally (Indiv)
# W means the action also affects the environment (Peeps or Grid)
class Action(Enum):
    MOVE_X= auto()                 # W +- X component of movement
    MOVE_Y= auto()                 # W +- Y component of movement
    MOVE_FORWARD= auto()           # W continue last direction
    MOVE_RL= auto()                # W +- component of movement
    MOVE_RANDOM= auto()            # W
    SET_OSCILLATOR_PERIOD= auto()  # I
    SET_LONGPROBE_DIST= auto()     # I
    SET_RESPONSIVENESS= auto()     # I
    EMIT_SIGNAL0= auto()           # W
    MOVE_EAST= auto()              # W
    MOVE_WEST= auto()              # W
    MOVE_NORTH= auto()             # W
    MOVE_SOUTH= auto()             # W
    MOVE_LEFT= auto()              # W
    MOVE_RIGHT= auto()             # W
    MOVE_REVERSE= auto()           # W
    KILL_FORWARD= auto()           # W
    NUM_ACTIONS= auto()     # <<----------------- END OF ACTIVE ACTIONS MARKER

def sensorName(sensor: Sensor):
    '''
    This converts sensor numbers to descriptive strings.
    '''
    match sensor.name:
        case 'AGE': return "age" 
        case 'BOUNDARY_DIST': return "boundary dist" 
        case 'BOUNDARY_DIST_X': return "boundary dist X" 
        case 'BOUNDARY_DIST_Y': return "boundary dist Y" 
        case 'LAST_MOVE_DIR_X': return "last move dir X" 
        case 'LAST_MOVE_DIR_Y': return "last move dir Y" 
        case 'LOC_X': return "loc X" 
        case 'LOC_Y': return "loc Y" 
        case 'LONGPROBE_POP_FWD': return "long probe population fwd" 
        case 'LONGPROBE_BAR_FWD': return "long probe barrier fwd" 
        case 'BARRIER_FWD': return "short probe barrier fwd-rev" 
        case 'BARRIER_LR': return "short probe barrier left-right" 
        case 'OSC1': return "osc1" 
        case 'POPULATION': return "population" 
        case 'POPULATION_FWD': return "population fwd" 
        case 'POPULATION_LR': return "population LR" 
        case 'RANDOM': return "random" 
        case 'SIGNAL0': return "signal 0" 
        case 'SIGNAL0_FWD': return "signal 0 fwd" 
        case 'SIGNAL0_LR': return "signal 0 LR" 
        case 'GENETIC_SIM_FWD': return "genetic similarity fwd" 
        case _: assert(False) 

def actionName(action: Action):
    '''
    Converts action numbers to descriptive strings.
    '''
    match action.name:
        case 'MOVE_EAST': return "move east" 
        case 'MOVE_WEST': return "move west" 
        case 'MOVE_NORTH': return "move north" 
        case 'MOVE_SOUTH': return "move south" 
        case 'MOVE_FORWARD': return "move fwd" 
        case 'MOVE_X': return "move X" 
        case 'MOVE_Y': return "move Y" 
        case 'SET_RESPONSIVENESS': return "set inv-responsiveness" 
        case 'SET_OSCILLATOR_PERIOD': return "set osc1" 
        case 'EMIT_SIGNAL0': return "emit signal 0" 
        case 'KILL_FORWARD': return "kill fwd" 
        case 'MOVE_REVERSE': return "move reverse" 
        case 'MOVE_LEFT': return "move left" 
        case 'MOVE_RIGHT': return "move right" 
        case 'MOVE_RL': return "move R-L" 
        case 'MOVE_RANDOM': return "move random" 
        case 'SET_LONGPROBE_DIST': return "set longprobe dist" 
        case _: assert(False)

def printSensorsActions():
    '''
    List the names of the active sensors and actions to stdout.
    "Active" means those sensors and actions that are compiled into
    the code. See the Sensor and Action classes for how to define the enums.
    '''
    print("Sensors:")
    for i in Sensor:
        print("  ", sensorName(i)) if i.value < Sensor.NUM_SENSES.value else 0
    
    print("Actions:")
    for i in Action:
        print("  ", actionName(i)) if i.value < Action.NUM_ACTIONS.value else 0

    # print("Sensors:")
    # for i in range(Sensor.NUM_SENSES.value):
    #     print("  ", sensorName(Sensor[i]))
    
    # print("Actions:")
    # for i in range(Action.NUM_ACTIONS.value):
    #     print("  ", actionName(i))
    
    print()

if __name__ == "__main__":
    for i in range(Sensor.NUM_SENSES.value):
        print(i)
    for i in range(Action.NUM_ACTIONS.value):
        print(i)
    printSensorsActions()