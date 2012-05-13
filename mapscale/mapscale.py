#!/usr/bin/env python
# encoding: utf-8
"""
ZeroMQ-based embarassingly parallel processing tool.
"""

import time
from  multiprocessing import Process

import zmq


class Processor(object):
    """Client/pool for distributing posterior function calls to workers and
    receiving results.

    We use the ventilator (or PUSH/PULL) design pattern.
    See http://zguide.zeromq.org/page:all#Divide-and-Conquer
    """
    def __init__(self, lnpostfn, nWorkers):
        super(Processor, self).__init__()
        self.lnpostfn = lnpostfn
        self.ventPort = "5557"
        self.collectorPort = "5558"
        self.controlPort = "5559"
        self.wakePort = "5560"
        self.bundlerPort = "5561"
        # Create local workers
        for i in range(nWorkers):
            Process(target=worker,
                    args=(lnpostfn, "127.0.0.1", self.ventPort,
                          self.collectorPort, self.controlPort))

        mktcp = lambda ip, port: "tcp://%s:%s" % (ip, port)
        self.context = zmq.Context()
        print self.context

        # Socket for controlling workers (ie shutdown)
        print mktcp("*", self.controlPort)
        self.controlSocket = self.context.socket(zmq.PUB)
        self.controlSocket.bind(mktcp("127.0.0.1", self.controlPort))

        # Create socket for sending jobs to workers
        self.ventSocket = self.context.socket(zmq.PUSH)
        self.ventSocket.bind(mktcp("127.0.0.1", self.ventPort))

        # Socket for telling receiver to start listening for results from
        # N jobs
        # ZMQProcessor acts as a client here; receiver is server
        self.wakeReceiverSocket = self.context.socket(zmq.REQ)
        self.wakeReceiverSocket.connect(mktcp("127.0.0.1", self.wakePort))

        # Socket for getting results from the receiver
        self.bundlerSocket = self.context.socket(zmq.REP)
        self.bundlerSocket.connect(mktcp("127.0.0.1", self.bundlerPort))

        # Setup receiver
        resultCollector = Process(target=result_collector,
                                  args=(self.collectorPort,
                                        self.wakeReceiverSocket,
                                        self.bundlerSocket))
        resultCollector.start()

    def add_remote_workers(self, host, port, nWorkers):
        """Adds workers on a remote machine; these are in addition to any
        local workers created when the instance was created.

        PyZMQ handles the communications for us; the hard part is
        instantiating these remote works. Probaby needs an SSH link
        and that the remote machine has a copy of the software in place.
        Perhaps even a copy of the lnpost function?
        """
        pass

    def shutdown(self):
        """Send a shutdown message to all work servers."""
        self.controlSocket.send("QUIT")

    def map(self, foo, jobList):
        """Allows `ZMQProcessor` to be used as a drop-in replacement
        for `multiprocessing`'s Pool.map().
        """
        pass

    def __call__(self, jobList):
        """Run jobs across all workers and return results in the same order."""
        nJobs = len(jobList)

        # TODO always start new result collector
        # or can it be reused?
        # If I set up a channel to talk between the main thread
        # and the result collector, I can pass nJobs, and later
        # ask for the jobs to be sent back
        # In this case the result collector would be created
        # upon init

        # Tell the receiver to expect new jobs
        self.wakeReceiverSocket.send_pyobj(nJobs)
        # receiver tells us its ready
        msg = self.coordinatorSocket.recv()

        # messages consist of (int, job_object)
        for message in enumerate(jobList):
            self.ventSocket.send_pyobj(message)

        # Receive result bundle from collector
        # Blocks until the resutls are transmitted
        results = self.bundlerSocket.recv_pyobj()
        self.bundlerSocket.send("THANKS")

        # Re-order results
        # jobIDs = [r[0] for r in results]
        # values = [r[1] for r in results]
        jobIDs, values = zip(*results)  # make sure this trick works?
        return sorted(values)


def worker(lnpostfn, clientIP, ventPort, collectorPort, controlPort):
    """Work server.
    
    Parameters
    ----------
    lnpostfn
        Callable instance that accepts a paraeter set and returns probability.
        `lnpostfn` may also have `setup()` and `cleanup()` methods to setup
        and clean up the computing environment.
    clientIP : str
        IP of the client. e.g. localhost
    ventPort : str
        Port that the ventilator communicates over
    collectorPort : str
        Port that the collector communicates over
    controlPort : str
        Port that the controller communicates over.
    """
    print "Booting up worker"
    # TODO check if lnpostfn has setup attribute first
    lnpostfn.setup()  # allow the posterior function to setup environment

    context = zmq.Context()

    # Socket to receive work from ventilator
    mktcp = lambda ip, port: "tcp://%s:%s" % (ip, port)
    workReceiver = context.socket(zmq.PULL)
    workReceiver.connect(mktcp(clientIP, ventPort))

    # Socket to send results to collector
    senderSocket = context.socket(zmq.PUSH)
    senderSocket.connect(mktcp(clientIP, collectorPort))

    # Socket to receive control signals over
    controlReceiver = context.socket(zmq.SUB)
    controlReceiver.connect(mktcp(clientIP, controlPort))
    controlReceiver.setsockopt(zmq.SUBSCRIBE, "")

    # zmq.Poller lets us multiplex the job receiver and control subscriptions
    poller = zmq.Poller()
    poller.register(workReceiver, zmq.POLLIN)
    poller.register(controlReceiver, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())

        if socks.get(workReceiver) == zmq.POLLIN:
            jobID, modelParams = workReceiver.recv_pyobj()
            # Call the posterior function
            lnprob = lnpostfn(modelParams)
            senderSocket.send_pyobj((jobID, lnprob))

        if socks.get(controlReceiver) == zmq.POLLIN:
            controlMessage = controlReceiver.recv()
            if controlMessage == "QUIT":
                # TODO check if lnppostfn has cleanup attribute
                lnpostfn.cleanup()
                break


def result_collector(collectorPort, wakePort, bundlerPort):
    """Receives results from the workers."""
    context = zmq.Context()

    mktcp = lambda ip, port: "tcp://%s:%s" % (ip, port)

    # Socket to receive results from the workers
    collector = context.socket(zmq.PULL)
    collector.bind(mktcp("127.0.0.1", collectorPort))

    # Socket to receive wake signals with number of jobs to expect
    wakeSocket = context.socket(zmq.REP)
    wakeSocket.bind(mktcp("127.0.0.1", wakePort))

    # Socket to send result list back
    bundlerSocket = context.socket(zmq.REQ)
    bundlerSocket.connect(mktcp("127.0.0.1", bundlerPort))

    while True:
        results = []

        nJobs = wakeSocket.recv_pyobj()
        wakeSocket.send("READY")

        for i in xrange(nJobs):
            resultMessage = collector.recv_pyobj()
            results.append(resultMessage)

        bundlerSocket.send_pyobj(results)
        msg = bundlerSocket.recv()


def main():
    pass


if __name__ == '__main__':
    main()
