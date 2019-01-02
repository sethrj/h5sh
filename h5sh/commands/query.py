# -*- coding: utf-8 -*-

"""Functions for querying data on an HDF5 file."""

from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
import numpy as np
from pprint import pformat
import sys
from time import time

from h5sh.utils import (make_column_kv_fmt, extract, format_shape)
from .base import Command
from .registry import register
###############################################################################

class Dump(Command):
    name = "dump"
    STDOUT = "STDOUT"

    def build_parser(self):
        parser = super(Dump, self).build_parser(
            description="Print the contents of a dataset")
        parser.add_argument('-A', '--onlyattr',
            help="Print only attributes",
            action="store_true")
        parser.add_argument('-p', '--precision', type=int, default=4,
            help="Floating point precision")
        parser.add_argument('-t', '--threshold', type=int, default=50,
            help="Number of values to display")
        parser.add_argument( '--suppress_small',
            help="Print very small numbers as zero",
            action="store_true")
        parser.add_argument('dataset', help="Dataset to print")
        parser.add_argument('-o', '--out',
            help="File to save output",
            default=Dump.STDOUT)
        return parser

    def execute(self, state, dataset, out, **kwargs):
        try:
            dataset = state.group[dataset]
        except KeyError:
            raise ValueError("Nonexistent dataset {!r}".format(dataset))

        if out == Dump.STDOUT:
            self._dump(dataset, sys.stdout, **kwargs)
        else:
            with open(out, 'w') as f:
                self._dump(dataset, f, **kwargs)

    def _dump(self, item, f, onlyattr, **kwargs):
        try:
            shape = item.shape
        except AttributeError:
            raise ValueError("{} is not a dataset".format(item.name))

        # Print size and shape
        f.write("Dataset: {}\n".format(item.name))
        f.write("Shape: {}".format(format_shape(shape)))
        if shape != item.maxshape:
            f.write("of max {}".format(format_shape(item.maxshape)))
        f.write("\n")

        # Print datatype
        dt = item.dtype
        if dt.names:
            # Write compound type in detail
            f.write("Type:\n")
            f.write(pformat(dt.descr))
        else:
            f.write("Type: {}\n".format(dt.name))

        # Print attributes
        attrs = dict(item.attrs)
        if attrs:
            f.write("Attributes:\n")
            f.write(pformat(attrs))

        # Print chunking
        if item.chunks:
            f.write("Chunked: {}\n".format(format_shape(item.chunks)))

        if item.compression:
            f.write("Compressed: {}\n".format(item.compression))

        if onlyattr:
            return

        threshold = kwargs['threshold']
        if item.size > threshold:
            # More than 60 lines, roughly
            print("Truncating dataset ({:d} exceeds threshold {:d}): "
                  "use -t to increase".format(item.size, threshold), file=f)
            # Set edge items so that approximately "threshold" will appear:
            # e.g. if dimension is 3, then take cube root of half the threshold
            kwargs['edgeitems'] = max(1, int(pow(threshold/2, 1/len(shape))))

        print("---", file=f)

        item = extract(item)
        if shape:
            # Print array with given options
            print(np.array2string(item, **kwargs), file=f)
        else:
            print(item, file=f)


register.instance(Dump)

###############################################################################

class Attrs(Command):
    name = "attr"

    def build_parser(self):
        parser = super(Attrs, self).build_parser(
            description="Print attributes of the current group or a given "
            "object")
        parser.add_argument('object', nargs='?')
        return parser

    def execute(self, state, obj=None):
        if obj is not None:
            obj = state.group[obj]
        else:
            obj = state.group

        attrs = obj.attrs
        keys = sorted(attrs)
        if not keys:
            return

        fmt = make_column_kv_fmt(keys, sep="=")
        for k in keys:
            v = to_native_str(attrs[k])
            print(fmt(k, v))

register.instance(Attrs)

