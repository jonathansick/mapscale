Basic Usage
===========

Writing Work Functions
----------------------

Like `multiprocessing`, your work functions take a single argument (the job) and return a single result.
In MapScale, we take the idea further, by requiring that work functions be *callable class instances*.
This allows us to have flexible initializations to package data required by all workers, have setup and destruction methods to prepare each worker instance *in situ*.

MapScale work classes follow a common interface::
    
    class WorkFunction(object):
        """A function that we want to compute in parallel. Data can be packaged
        into the workers during `__init__`, that will be available to all
        worker instances.
        """
        def __init__(self, args):
            super(WorkFunction, self).__init__()
            self.args = args

        def __call__(self, x):
            """Your call method takes a single argument with the job
            data. This can be any python object (numpy arrays, lists, etc.)
            """
            return x ** 2.

        def setup(self):
            """The setup method will be run once for each worker instance.
            This is your chance to setup a worker's environment (cache
            data from disk, etc.)
            """
            print "Setting up"

        def cleanup(self):
            """The cleanup method is called once for each worker instance
            when the user tells the MapScale processor to shutdown. This is
            your chance to release any resources used by the worker, such
            as temporary files.
            """
            print "Cleaning up"

Running MapScale with your Worker Function
------------------------------------------

Once you have a work function, you can setup a MapScale processor, as so::

    from mapscale import Processor
    myfunc = WorkFunction()
    mapper = Processor(myfunc, 2)

Here the `mapper` is a :class:`Processor` instance that bakes the work function in.
The second argument is the number of workers you want to create on your `localhost`; two in this case.

The `mapper` is equivalent to Python's built-in :func:`map` function, *except* that you only need to pass an iterable list of jobs for the worker function to process each job--the worker function is already baked in!
That is::

    jobList = range(5)
    results = mapper(jobList)

Here the job queue consists of a list of five integers (`jobList`).
The `results` are now a list of five results, in the same order as your `jobList` (just like running a Python :func:`map`).
And that's it!

But there's one last thing. Your worker functions are still alive.
Think of workers as server processes that return a result whenever called.
This design is beneficial because we can run `mapper(jobList)` a second (or Nth) time without having to setup the worker pool again (which is why we're using MapScale in the first place), but it means we need to manually shutdown the worker servers.
To do this, we shut them down::

    mapper.shutdown()

Once this is done, the work servers are shutdown, their `cleanup()` methods called, and `mapper` itself is rendered inert.
