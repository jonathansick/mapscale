MapScale
========

Use MapScale for embarrassingly parallel python pipelines.
The use pattern is similar to `multiprocessing`'s Pool.map().
MapScale uses the ZeroMQ messaging framework, allow jobs to be distributed across a network, and allows persistent job servers to reduce setup latency.
