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
        parser.add_argument(
            '--suppress',
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
        padlen = max(len(s) for s in (item.name, "Attributes"))
        format_key = ("{{:{:d}s}}:".format(padlen)).format
        print(format_key(item.name), format_shape(shape), file=f)

        # Print datatype
        dt = item.dtype
        print(format_key("Type"), pformat(dt.descr) if dt.names else dt.name,
              file=f)

        # Print attributes
        attrs = dict(item.attrs)
        if attrs:
            print(format_key("Attributes"), pformat(attrs), file=f)

        # Print chunking
        if item.chunks:
            print(format_key("Chunked"), item.chunks, file=f)

        if onlyattr:
            return

        if f.isatty() and item.size > 60 * 5:
            # More than 60 lines, roughly
            print("Dataset is too large to display; use '-o' flag "
                  "to save to a file", file=f)
            return

        item = extract(item)
        if shape:
            # Print array with given options
            # (Use instead of array2string because of embedded objects)
            with np.printoptions(**kwargs):
                print(item, file=f)
        else:
            print(item, file=f)


register.instance(Dump)

###############################################################################

class Attrs(Command):
    name = "attr"

    def build_parser(self):
        parser = super(Attrs, self).build_parser(
            description="Print attributes of the current group")
        return parser

    def execute(self, state, daughter=None):
        group = state.group
        if daughter is not None:
            group = group[daughter]

        attrs = group.attrs
        keys = sorted(attrs)
        if not keys:
            return

        fmt = make_column_kv_fmt(keys, sep="=")
        for k in keys:
            v = to_native_str(attrs[k])
            print(fmt(k, v))

register.instance(Attrs)

