.. ############################################################################
.. File  : h5sh/docs/introduction.rst
.. ############################################################################

************
Introduction
************

This project was motivated by both technical and user requirements.
First, when using ``h5ls`` on parallel filesystems with very large data files,
I found the performance to be abysmal for even a single application of
``h5ls``. Second, when introducing HDF5-formatted output files to engineering
analysts used to large ASCII text files, an intuitive way of accessing the
output data was needed to lower their barrier to entry. The ``h5sh`` utility
attempts to solve both of these problems by providing an efficient tool to
naturally explore arbitrarily large HDF5 data files.

.. ............................................................................

Installation
============

As of this writing, ``h5sh`` has not been submitted to PyPI, so it must be
installed from source.

Stable release
--------------

To install h5sh, run this command in your terminal:

.. code-block:: console

    $ pip install h5sh

This is the preferred method to install h5sh, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for h5sh can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/sethrj/h5sh

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/sethrj/h5sh/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/sethrj/h5sh
.. _tarball: https://github.com/sethrj/h5sh/tarball/master

.. ............................................................................

Usage
=====

This package is meant to be used through the command-line interface (CLI) via
the ``h5sh`` command.


.. ----------------------------------------------------------------------------
.. CONTRIBUTING
.. ----------------------------------------------------------------------------

.. include:: ../CONTRIBUTING.rst

.. ############################################################################
.. end of h5sh/docs/introduction.rst
.. ############################################################################
