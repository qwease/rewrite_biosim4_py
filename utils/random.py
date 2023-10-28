# encoding: utf-8
import threading
from typing import Optional
import random
import time

class RandomUintGenerator:
    def __init__(self):
        # for the Marsaglia algorithm
        self.rngx = 0
        self.rngy = 0
        self.rngz = 0
        self.rngc = 0
        # for the Jenkins algorithm
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0

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
            thread_num = threading.get_ident()
            self.rngx = params.RNGSeed + 123456789 + thread_num
            self.rngy = params.RNGSeed + 362436000 + thread_num
            self.rngz = params.RNGSeed + 521288629 + thread_num
            self.rngc = params.RNGSeed + 7654321 + thread_num
            self.rngx = self.rngx if self.rngx != 0 else 123456789
            self.rngy = self.rngy if self.rngy != 0 else 123456789
            self.rngz = self.rngz if self.rngz != 0 else 123456789
            self.rngc = self.rngc if self.rngc != 0 else 123456789

            # Initialize Jenkins deterministically per-thread:
            self.a = 0xf1ea5eed
            self.b = self.c = self.d = params.RNGSeed + thread_num
            if self.b == 0:
                self.b = self.c = self.d + 123456789
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
            self.rngx = random.getrandbits(32) or 123456789
            self.rngy = random.getrandbits(32) or 123456789
            self.rngz = random.getrandbits(32) or 123456789
            self.rngc = random.getrandbits(32) or 123456789

            # Initialize Jenkins, but don't let any of the values be zero:
            self.a = 0xf1ea5eed
            self.b = self.c = self.d = random.getrandbits(32) or 123456789

    def __call__(self, min: Optional[int] = None, max: Optional[int] = None) -> int:
        if min is None or max is None:
            # return a random uint32_t
            pass
        else:
            # return a random number between min and max (inclusive)
            pass

# The globally-scoped random number generator.
# Each thread will have a private instance.
randomUint = threading.local()
randomUint.instance = RandomUintGenerator()

RANDOM_UINT_MAX = 0xffffffff