What can MapScale do for me?
============================

We all know the drill.
Our pipelines are embarassingly parallel; our datasets are massive, and our computers are stocked with cores.
So we reach for Python's :mod:`multiprocessing` module::

    import multiprocessing
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    results = pool.map(my_pipeline_function, job_list)

This works great, but there are two limitations:

1. **Pickling overhead.** Your pipeline function needs to be pickled and unpickled for every work process. For one-off `map` queues this is acceptable, but some loosely coupled parallel algorithms require several bursts of map jobs based on the previous job pool. A good example is the `emcee` ensemble sampling code: a large pool of walkers explore multiple points in parameter space in parallel; a new set of points is chosen, and the posterior is again sampled in parallel. In this case, worker functions are pickled and pickled for each map iteration. Can't we just pickle the mapping function once on setup, and treat the workers as servers? MapScale does this thanks to the ZeroMQ messaging framework.
2. **Scalability.** Multiprocessing works fine within a single box; but what if we want to tap into the processing power of other computers on our network? For this you need a multiprocessing framework that understands TCP. Thanks for ZeroMQ, MapScale talks over TCP.
