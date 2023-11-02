# encoding: utf-8

# random.py
# This file provides a random number generator (RNG) suitable for use in both the main thread
# and any child threads. The global RNG instance, named randomUint, is unique for each thread, ensuring thread safety.
# Python automatically creates a new instance for each thread, 
# thus eliminating the need for explicit thread-private declarations as seen in languages like C++ with OpenMP.
# Due to the nature of Python's object model, the RNG object doesn't require a complex constructor.
# Instead, we use an initialize() member function to seed the RNG. 
# This function is typically called within simulator() in simulator.py once the configuration parameters have been read.
# The parameter's deterministic and RNGSeed from the configuration file biosim4.ini dictate the mode of RNG initialization.
# When deterministic is True, the RNG is initialized with a deterministic seed defined by RNGSeed.
# When deterministic is False, the RNG is initialized with a random seed.

import threading
from typing import Optional
import random
import time

from ctypes import c_uint32
from sys import path
from path import Path
# caution: path[0] is reserved for script path (or '' in REPL)
if str(Path(__file__).parent.parent) not in path:
    path.append(str(Path(__file__).parent.parent))
# print(sys.path)
from params import Params 

class RandomUintGenerator:
    rngx:c_uint32
    rngy:c_uint32
    rngz:c_uint32
    rngc:c_uint32

    a:c_uint32
    b:c_uint32
    c:c_uint32
    d:c_uint32

    def __init__(self):
        # for the Marsaglia algorithm
        self.rngx = c_uint32(0)
        self.rngy = c_uint32(0)
        self.rngz = c_uint32(0)
        self.rngc = c_uint32(0)
        # for the Jenkins algorithm
        self.a = c_uint32(0)
        self.b = c_uint32(0)
        self.c = c_uint32(0)
        self.d = c_uint32(0)
        self.isInitialised=False # try to initialise once for one thread

    def initialize(self, params):
        '''
        must be called to seed the RNG
        '''
        
        thread_num_temp = c_uint32(threading.get_ident()) # check if unique only in development
        # if p.deterministic:
        if not self.isInitialised:
            if params.deterministic:
                # Initialize Marsaglia. Overflow wrap-around is ok. We just want
                # the four parameters to be unrelated. In the extremely unlikely
                # event that a coefficient is zero, we'll force it to an arbitrary
                # non-zero value. Each thread uses a different seed, yet
                # deterministic per-thread.
                thread_num = c_uint32(threading.get_ident())
                self.rngx = c_uint32(params.RNGSeed + 123456789 + thread_num.value)
                self.rngy = c_uint32(params.RNGSeed + 362436000 + thread_num.value)
                self.rngz = c_uint32(params.RNGSeed + 521288629 + thread_num.value)
                self.rngc = c_uint32(params.RNGSeed + 7654321 + thread_num.value)
                self.rngx = self.rngx if self.rngx != c_uint32(0) else c_uint32(123456789)
                self.rngy = self.rngy if self.rngy != c_uint32(0) else c_uint32(123456789)
                self.rngz = self.rngz if self.rngz != c_uint32(0) else c_uint32(123456789)
                self.rngc = self.rngc if self.rngc != c_uint32(0) else c_uint32(123456789)
                # Initialize Jenkins deterministically per-thread:
                self.a = c_uint32(0xf1ea5eed)
                self.b = self.c = self.d = c_uint32(params.RNGSeed + thread_num.value)
                if self.b.value == 0:
                    self.b = self.c = self.d.value + c_uint32(123456789)
            else:
                # Non-deterministic initialization.
                # First we will get a random number from the built-in random
                # generator and use that to derive the starting coefficients 
                # for the Marsaglia and Jenkins RNGs.
                # We'll seed random with time(), but that has a coarse
                # resolution and multiple threads might be initializing their
                # instances at nearly the same time, so we'll add the thread
                # number to uniquely seed random per-thread.
                random.seed(int(time.time()) + threading.get_ident())

                # Initialize Marsaglia, but don't let any of the values be zero:
                self.rngx = c_uint32(random.getrandbits(32)) or c_uint32(123456789)
                self.rngy = c_uint32(random.getrandbits(32)) or c_uint32(123456789)
                self.rngz = c_uint32(random.getrandbits(32)) or c_uint32(123456789)
                self.rngc = c_uint32(random.getrandbits(32)) or c_uint32(123456789)

                # Initialize Jenkins, but don't let any of the values be zero:
                self.a = c_uint32(0xf1ea5eed)
                self.b = self.c = self.d = c_uint32(random.getrandbits(32)) or c_uint32(123456789)
        print(thread_num_temp.value) # check if unique only in development
        self.isInitialised = True

    def __call__(self, min: Optional[c_uint32] = None, max: Optional[c_uint32] = None, algo: bool = 0) -> c_uint32:
        # algo: 
        # 0: Jenkins algorithm
        # 1: Marsaglia algorithm
        if min is None or max is None:
            # This is equivalent to the C++ operator() method with no arguments
            if algo:  # Replace with a condition to choose between the two algorithms
                # Marsaglia algorithm
                a = 698769069
                self.rngx = c_uint32(69069 * self.rngx.value + 12345)
                self.rngy.value ^= c_uint32(self.rngy.value << 13).value
                self.rngy.value ^= c_uint32(self.rngy.value >> 17).value
                self.rngy.value ^= c_uint32(self.rngy.value << 5).value  # you must never be set to zero!
                t = c_uint32(a * self.rngz.value + self.rngc.value)
                self.rngc = c_uint32(t.value >> 32)  # Also avoid setting z=c=0!
                return c_uint32(self.rngx.value + self.rngy.value + (self.rngz.value == t.value))
            else:
                # Jenkins algorithm (Faster)
                rot32 = lambda x, k: (((x) << (k)) | ((x) >> (32 - (k))))
                e = c_uint32(self.a.value - rot32(self.b.value, 27))
                self.a = c_uint32(self.b.value ^ rot32(self.c.value, 17))
                self.b = c_uint32(self.c.value + self.d.value)
                self.c = c_uint32(self.d.value + e.value)
                self.d = c_uint32(e.value + self.a.value)
                return c_uint32(self.d.value)
        else:
            # This is equivalent to the C++ operator() method with min and max arguments
            if isinstance(max, int) and isinstance(min,int):
                max_,min_=c_uint32(max),c_uint32(min)
            else:
                max_,min_=max, min
            assert max_.value >= min_.value
            return c_uint32((self.__call__(algo=algo).value % (max_.value - min_.value + 1)) + min_.value)

randomUint = threading.local()


if __name__ == "__main__":
    def thread_function(thread_id):
        randomUint.instance = RandomUintGenerator()
        randomUint.instance.initialize(params=params)
        print(f'Thread-{thread_id} value: ', randomUint.instance(algo=0))
    
    # The globally-scoped random number generator.
    # Each thread will have a private instance of the RNG.
    from simulator import params
    # randomUint.instance = RandomUintGenerator()
    # randomUintInst = randomUint.instance.initialize(params=params)

    threads = []

    import time
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
    print(end-start)