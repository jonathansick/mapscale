.. MapScale documentation master file, created by
   sphinx-quickstart on Sat May 19 16:30:00 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MapScale
========

MapScale is a Python tool for embarrassingly parallel python workflows.
It works like Python's built-in `multiprocessing`_ `Pool.map()`, except MapScale uses `ZeroMQ`_ messaging to create work servers.
This lets you reduce overhead--workers are setup just once, and can be re-used with several map calls--and allows you to add workers from across the Internet.

MapScale is being developed at https://www.github.com/jonathansick/mapscale.
To install::

    git clone https://github.com/jonathansick/mapscale.git
    cd mapscale
    python setup.py install

Note, you will need to also install `pyzmq`_.

Contents
--------

.. toctree::
   :maxdepth: 2
   
   intro
   basic



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _ZeroMQ: http://www.zeromq.org
.. _multiprocessing: http://docs.python.org/library/multiprocessing.html#using-a-pool-of-workers
.. _pyzmq: http://zeromq.github.com/pyzmq/
