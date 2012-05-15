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
            print "Making worker"
            Process(target=worker,
                    args=(lnpostfn, "127.0.0.1", self.ventPort,
                          self.collectorPort, self.controlPort)).start()

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
        self.bundlerSocket.bind(mktcp("127.0.0.1", self.bundlerPort))

        # Setup receiver
        resultCollector = Process(target=result_collector,
                                  args=(self.collectorPort,
                                        self.wakePort,
                                        self.bundlerPort))
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

    def shutdown(self, sleep=1.):
        """Send a shutdown message to all work servers."""
        self.controlSocket.send("QUIT")
        self.wakeReceiverSocket.send_pyobj("QUIT")

        # time.sleep(sleep)
        self.controlSocket.setsockopt(zmq.LINGER, 0)
        self.wakeReceiverSocket.setsockopt(zmq.LINGER, 0)
        self.bundlerSocket.setsockopt(zmq.LINGER, 0)
        self.ventSocket.setsockopt(zmq.LINGER, 0)
        self.controlSocket.close()
        self.wakeReceiverSocket.close()
        self.bundlerSocket.close()
        self.ventSocket.close()
        # time.sleep(sleep)

    def map(self, foo, jobList):
        """Allows `ZMQProcessor` to be used as a drop-in replacement
        for `multiprocessing`'s Pool.map().
        """
        pass

    def __call__(self, jobList):
        """Run jobs across all workers and return results in the same order."""
        nJobs = len(jobList)

        # Tell the receiver to expect new jobs
        self.wakeReceiverSocket.send_pyobj(nJobs)
        # receiver tells us its ready
        msg = self.wakeReceiverSocket.recv()

        # messages consist of (int, job_object)
        for message in enumerate(jobList):
            self.ventSocket.send_pyobj(message)

        # Receive result bundle from collector
        # Blocks until the resutls are transmitted
        results = self.bundlerSocket.recv_pyobj()
        self.bundlerSocket.send("THANKS")

        # Re-order results
        # results is a list of (jobID, value), so that sorting of results
        # will automatically key on jobID
        results.sort()
        # Nifty way to unzip
        jobIDs, values = zip(*results)
        return values


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
                workReceiver.setsockopt(zmq.LINGER, 0)
                senderSocket.setsockopt(zmq.LINGER, 0)
                controlReceiver.setsockopt(zmq.LINGER, 0)
                workReceiver.close()
                senderSocket.close()
                controlReceiver.close()
                break


def result_collector(collectorPort, wakePort, bundlerPort):
    """Receives results from the workers."""
    print "result_collector booting up"
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

        msg = wakeSocket.recv_pyobj()

        if msg == "QUIT":
            print("result_collector shutting down")
            wakeSocket.send("result_collector shutting down")
            collector.setsockopt(zmq.LINGER, 0)
            wakeSocket.setsockopt(zmq.LINGER, 0)
            bundlerSocket.setsockopt(zmq.LINGER, 0)
            collector.close()
            wakeSocket.close()
            bundlerSocket.close()
            break
        else:
            nJobs = int(msg)
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
