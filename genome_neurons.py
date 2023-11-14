# encoding: utf-8

from sys import path
import threading
from path import Path
# caution: path[0] is reserved for script path (or '' in REPL)
if str(Path(__file__).parent) not in path:
    path.append(str(Path(__file__).parent)) 
# print(sys.path)
from utils.RNG import getRandomGenerator#RandomUintGenerator,randomUint
# from simulator import params
from params import params

# Each gene specifies one synaptic connection in a neural net. Each
# connection has an input (source) which is either a sensor or another neuron.
# Each connection has an output, which is either an action or another neuron.
# Each connection has a floating point weight derived from a signed 16-bit
# value. The signed integer weight is scaled to a small range, then cubed
# to provide fine resolution near zero.

# Constants
SENSOR = 1  # always a source
ACTION = 1  # always a sink
NEURON = 0  # can be either a source or sink

class Gene:
    def __init__(self, sourceType, sourceNum, sinkType, sinkNum, weight):
        self.sourceType = sourceType  # SENSOR or NEURON value 1
        self.sourceNum = sourceNum # value 7
        self.sinkType = sinkType  # NEURON or ACTION value 1
        self.sinkNum = sinkNum # value 7
        self.weight = weight

    @property
    def weightAsFloat(self):
        f1: float = 8.0
        f2: float = 64.0
        return self.weight / 8192.0

    @staticmethod
    def makeRandomWeight() -> float:
        # been wrapped by outer thread
        
        # randomUint.instance = RandomUintGenerator()
        # randomUint.instance.initialize(params=params)
        # return randomUint.instance(0, 0xffff).value - 0x8000
        randomUint = getRandomGenerator(p=params)
        return randomUint(0, 0xffff).value - 0x8000

# An individual's genome is a set of Genes (see Gene comments above). Each
# gene is equivalent to one connection in a neural net. An individual's
# neural net is derived from its set of genes.
Genome: [Gene] = list

# Each neuron has a single output which is
# connected to a set of sinks where each sink is either an action output
# or another neuron. 
# Each neuron has a set of input sources where each
# source is either a sensor or another neuron. 
# There is no concept of layers in the net: it's a free-for-all topology
# with forward, backwards,
# and sideways connection allowed. Weighted connections are allowed
# directly from any source to any action.

# Currently the genome does not specify the activation function used in
# the neurons. (May be hardcoded to tanh() !!!)

# TO-DO: activation functions, like Sigmoid

# When the input is a sensor, the input value to the sink is the raw
# sensor value of type float and depends on the sensor. If the output
# is an action, the source's output value is interpreted by the action
# node and whether the action occurs or not depends on the action's
# implementation.

# In the genome, neurons are identified by 15-bit unsigned indices,
# which are reinterpreted as values in the range 0..params.genomeMaxLength-1
# by taking the 15-bit index modulo the max number of allowed neurons.
# In the neural net, the neurons that end up connected get new indices
# assigned sequentially starting at 0.

class NeuralNet:
    class Neuron:
        def __init__(self):
            self.output: float = 0.0
            self.driven: bool = False  # undriven neurons have fixed output values

    def __init__(self):
        self.connections: [Gene] = []  # connections are equivalent to genes
        self.neurons = [] # of type [Neuron]

# When a new population is generated and every individual is given a
# neural net, the neuron outputs must be initialized to something:
def initialNeuronOutput() -> float:
    return 0.5

def makeRandomGene() -> Gene:
    pass

def makeRandomGenome() -> Genome:
    pass

def unitTestConnectNeuralNetWiringFromGenome():
    pass

def genomeSimilarity(g1: Genome, g2: Genome) -> float:  # 0.0..1.0
    pass

def geneticDiversity() -> float:  # 0.0..1.0
    pass

if __name__ == "__main__":
    # prove if an empty function could be rewrited in-file
    def geneticDiversity() -> float:  # 0.0..1.0
        return 0.3
    print(geneticDiversity())

    # multithread testing
    gene=Gene(1,7,1,7,0.1)
    def thread_function(thread_id):
        print(f'Thread-{thread_id} value: ', gene.makeRandomWeight())
    
    # The globally-scoped random number generator.
    # Each thread will have a private instance of the RNG.
    # from simulator import params
    from params import params
    # randomUint.instance = RandomUintGenerator()
    # randomUintInst = randomUint.instance.initialize(params=params)

    threads = []

    import time
    tests=[]
    for i in range(1):
        start = time.time()
        # Create and start 10 threads
        for i in range(10):
            t = threading.Thread(target=thread_function, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()
        
        end= time.time()

        tests.append(end-start)
    print(sum(tests)/len(tests))