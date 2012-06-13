# MapScale

Use MapScale for embarrassingly parallel python pipelines.
MapScale uses the ZeroMQ messaging framework, allows jobs to be distributed across a network, and allows persistent job servers to reduce setup latency.
The use pattern is similar to `multiprocessing`'s Pool.map().

MapScale lives at https://github.com/jonathansick/mapscale

## Documentation

One the web: [http://mapscale.jonathansick.ca](http://mapscale.jonathansick.ca).

On your computer:

    cd *mapscale repo*
    python setup.py docs

and documentation will be built in `build/sphinx/html`.

## Development TODO List

1. Add workers of the network, using TCP sockets in SSH tunnels.
   Currently, only local workers are supported.
2. Make sure that workers have completed their startup sequence before we give them jobs.
   This will require an update to the socket architecture.
3. Make MapScale robust to lost jobs and worker dropouts.
   This will be particuarly useful once we add workers over the internet.
4. Documentation, we need more of that.

## Development

Fork the [MapScale repo](http://www.github.com/jonathansick/mapscale) and send pull requests!
