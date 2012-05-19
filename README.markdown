MapScale
========

Use MapScale for embarrassingly parallel python pipelines.
The use pattern is similar to `multiprocessing`'s Pool.map().
MapScale uses the ZeroMQ messaging framework, allow jobs to be distributed across a network, and allows persistent job servers to reduce setup latency.

Documentation
-------------

One the web: [http://mapscale.jonathansick.ca](http://mapscale.jonathansick.ca).

On your computer:

    cd *mapscale repo*
    python setup.py docs

and documentation will be built in `build/sphinx/html`.

Development
-----------

Fork the [MapScale repo](http://www.github.com/jonathansick/mapscale) and send pull requests!

License
-------

Copyright 2012, Jonathan Sick
