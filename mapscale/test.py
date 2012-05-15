#!/usr/bin/env python
# encoding: utf-8
"""
Basic burn-in test.
"""

import time

from mapscale import Processor


def main():
    myfunc = WorkFunction()
    mapper = Processor(myfunc, 2)
    # time.sleep(2.)
    
    jobList = range(5)
    results = mapper(jobList)
    print results
    mapper.shutdown(sleep=1.)


class WorkFunction(object):
    """A function that we want to compute in parallel."""
    def __init__(self):
        super(WorkFunction, self).__init__()

    def __call__(self, x):
        """docstring for __call__"""
        # print x
        # time.sleep(1.)
        return x ** 2.

    def setup(self):
        """docstring for setup"""
        print "Setting up"

    def cleanup(self):
        """docstring for cleanup"""
        print "Cleaning up"

if __name__ == '__main__':
    main()
    main()
