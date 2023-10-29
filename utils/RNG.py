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

import ctypes

class RandomUintGenerator:
    rngx:ctypes.c_uint32
    rngy:ctypes.c_uint32
    rngz:ctypes.c_uint32
    rngc:ctypes.c_uint32

    a:ctypes.c_uint32
    b:ctypes.c_uint32
    c:ctypes.c_uint32
    d:ctypes.c_uint32

    def __init__(self):
        # for the Marsaglia algorithm
        self.rngx = ctypes.c_uint32(0)
        self.rngy = ctypes.c_uint32(0)
        self.rngz = ctypes.c_uint32(0)
        self.rngc = ctypes.c_uint32(0)
        # for the Jenkins algorithm
        self.a = ctypes.c_uint32(0)
        self.b = ctypes.c_uint32(0)
        self.c = ctypes.c_uint32(0)
        self.d = ctypes.c_uint32(0)

    def initialize(self, params):
        '''
        must be called to seed the RNG
        '''
        # if p.deterministic:
        if params.deterministic:
            # Initialize Marsaglia. Overflow wrap-around is ok. We just want
            # the four parameters to be unrelated. In the extremely unlikely
            # event that a coefficient is zero, we'll force it to an arbitrary
            # non-zero value. Each thread uses a different seed, yet
            # deterministic per-thread.
            thread_num = ctypes.c_uint32(threading.get_ident())
            self.rngx = ctypes.c_uint32(params.RNGSeed + 123456789 + thread_num.value)
            self.rngy = ctypes.c_uint32(params.RNGSeed + 362436000 + thread_num.value)
            self.rngz = ctypes.c_uint32(params.RNGSeed + 521288629 + thread_num.value)
            self.rngc = ctypes.c_uint32(params.RNGSeed + 7654321 + thread_num.value)
            self.rngx = self.rngx if self.rngx != ctypes.c_uint32(0) else ctypes.c_uint32(123456789)
            self.rngy = self.rngy if self.rngy != ctypes.c_uint32(0) else ctypes.c_uint32(123456789)
            self.rngz = self.rngz if self.rngz != ctypes.c_uint32(0) else ctypes.c_uint32(123456789)
            self.rngc = self.rngc if self.rngc != ctypes.c_uint32(0) else ctypes.c_uint32(123456789)

            # Initialize Jenkins deterministically per-thread:
            self.a = ctypes.c_uint32(0xf1ea5eed)
            self.b = self.c = self.d = ctypes.c_uint32(params.RNGSeed + thread_num.value)
            if self.b.value == 0:
                self.b = self.c = self.d.value + ctypes.c_uint32(123456789)
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
            self.rngx = ctypes.c_uint32(random.getrandbits(32)) or ctypes.c_uint32(123456789)
            self.rngy = ctypes.c_uint32(random.getrandbits(32)) or ctypes.c_uint32(123456789)
            self.rngz = ctypes.c_uint32(random.getrandbits(32)) or ctypes.c_uint32(123456789)
            self.rngc = ctypes.c_uint32(random.getrandbits(32)) or ctypes.c_uint32(123456789)

            # Initialize Jenkins, but don't let any of the values be zero:
            self.a = ctypes.c_uint32(0xf1ea5eed)
            self.b = self.c = self.d = ctypes.c_uint32(random.getrandbits(32)) or ctypes.c_uint32(123456789)

    def __call__(self,algo: bool = 0, min: Optional[ctypes.c_uint32] = None, max: Optional[ctypes.c_uint32] = None) -> ctypes.c_uint32:
        # algo: 
        # 0: Jenkins algorithm
        # 1: Marsaglia algorithm

        if min is None or max is None:
            # This is equivalent to the C++ operator() method with no arguments
            if algo:  # Replace with a condition to choose between the two algorithms
                # Marsaglia algorithm
                a = 698769069
                self.rngx = ctypes.c_uint32(69069 * self.rngx.value + 12345)
                self.rngy.value ^= ctypes.c_uint32(self.rngy.value << 13).value
                self.rngy.value ^= ctypes.c_uint32(self.rngy.value >> 17).value
                self.rngy.value ^= ctypes.c_uint32(self.rngy.value << 5).value  # you must never be set to zero!
                t = ctypes.c_uint32(a * self.rngz.value + self.rngc.value)
                self.rngc = ctypes.c_uint32(t.value >> 32)  # Also avoid setting z=c=0!
                return self.rngx.value + self.rngy.value + (self.rngz.value == t.value)
            else:
                # Jenkins algorithm (Faster)
                rot32 = lambda x, k: (((x) << (k)) | ((x) >> (32 - (k))))
                e = ctypes.c_uint32(self.a.value - rot32(self.b.value, 27))
                self.a = ctypes.c_uint32(self.b.value ^ rot32(self.c.value, 17))
                self.b = ctypes.c_uint32(self.c.value + self.d.value)
                self.c = ctypes.c_uint32(self.d.value + e.value)
                self.d = ctypes.c_uint32(e.value + self.a.value)
                return self.d.value
        else:
            # This is equivalent to the C++ operator() method with min and max arguments
            assert max.value >= min.value
            return (self.__call__().value % (max.value - min.value + 1)) + min.value

# The globally-scoped random number generator.
# Each thread will have a private instance of the RNG.
randomUint = threading.local()
randomUint.instance = RandomUintGenerator()

RANDOM_UINT_MAX = 0xffffffff

if __name__ == "__main__":
    class Params:
        def __init__(self) -> None:
            self.deterministic=True
            self.RNGSeed=0
    
    def thread_function(thread_id):
        randomUint.instance = RandomUintGenerator()
        randomUint.instance.initialize(params=Params())
        print(f'Thread-{thread_id} value: ', randomUint.instance(algo=0))

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