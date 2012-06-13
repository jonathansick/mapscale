# MapScale

Use MapScale for embarrassingly parallel python pipelines.
MapScale uses the ZeroMQ messaging framework, allows jobs to be distributed across a network, and allows persistent job servers to reduce setup latency.
The use pattern is similar to `multiprocessing`'s Pool.map().

MapScale lives at https://github.com/jonathansick/mapscale

## Documentation

On the web: [http://mapscale.jonathansick.ca](http://mapscale.jonathansick.ca).

You can also get [PDF](http://media.readthedocs.org/pdf/mapscale/latest/mapscale.pdf)
and [EPUB](http://media.readthedocs.org/epub/mapscale/latest/mapscale.epub) versions.
Thank you [Read the Docs](http://readthedocs.org/)!

To build the documentation on your computer:

    cd *mapscale repo*
    python setup.py docs

and documentation will be built in `build/sphinx/html`.

## Development

Fork the [MapScale repo](http://www.github.com/jonathansick/mapscale) and send pull requests!

### TODO List

1. Add workers of the network, using TCP sockets in SSH tunnels.
   Currently, only local workers are supported.
2. Make sure that workers have completed their startup sequence before we give them jobs.
   This will require an update to the socket architecture.
3. Make MapScale robust to lost jobs and worker dropouts.
   This will be particularly useful once we add workers over the Internet.
4. Documentation, we need more of that.
