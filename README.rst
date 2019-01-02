====
h5sh
====


.. image:: https://img.shields.io/pypi/v/h5sh.svg
        :target: https://pypi.python.org/pypi/h5sh

.. image:: https://img.shields.io/travis/sethrj/h5sh.svg
        :target: https://travis-ci.org/sethrj/h5sh

.. image:: https://readthedocs.org/projects/h5sh/badge/?version=latest
        :target: https://h5sh.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Fast shell-like tool for interacting with HDF5 files.

This tool is meant to replace repeated calls to ``h5ls`` and ``h5dump``, each
of which can take substantial amounts of time for large files. In contrast,
this utility only has to open a file once, doesn't have to read all the file
contents in order to browse or view attributes, and uses HDF5's internal
cacheing for speed.

The ``h5sh`` tool uses a shell-like interface so that analysts will find the
interface familiar.


* Free software: BSD license
* Documentation: https://h5sh.readthedocs.io.


Features
--------

* Tab-completion of commands, dataset names, and group names
* Dump datasets to screen or disk with the ``dump`` command
* Browse groups with ``cd`` and view attributes with ``attr``

License
-------

BSD license, see LICENSE.
