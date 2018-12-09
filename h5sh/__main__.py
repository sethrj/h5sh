# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function, )
import sys

def run(inp, debug=False):
    from .state import State
    from .console import Console
    with State(inp) as state:
        console = Console(state)
        console.debug = debug
        console.interact()


def main(argv=None):
    from argparse import ArgumentParser
    from exnihilotools import ENVIRONMENT

    # Load version

    scale_vers = ENVIRONMENT['scale_version']

    h5err = None
    try:
        from h5py import version as h5version
    except ImportError as e:
        h5err = e
        h5py_vers = hdf5_vers = "UNAVAILABLE"
    else:
        h5py_vers = h5version.version
        hdf5_vers = h5version.hdf5_version

    py_vers = "{v.major}.{v.minor}.{v.micro}".format(v=sys.version_info)
    version_str = "h5py {} [Python {}] [h5py {}] [HDF5 {}]".format(
        scale_vers, py_vers, h5py_vers, hdf5_vers)

    # Create parser

    parser = ArgumentParser(
        prog="h5sh",
        description="shell-like interface to interacting with HDF5 files")
    parser.add_argument('inp',
                        help="Name of the HDF5 input file")
    parser.add_argument('--version', action="version",
                        version=version_str)
    parser.add_argument('-g', '--debug', action="store_true")

    args = parser.parse_args(argv)

    if h5err is not None:
        # h5py is unavailable
        parser.error("The 'h5py' Python package is required to run this "
                     "utility: " + str(h5err))
        sys.exit(2)

    # Print the version string at the top
    print(version_str)

    # Run the program
    run(**vars(args))

if __name__ == '__main__':
    main()

