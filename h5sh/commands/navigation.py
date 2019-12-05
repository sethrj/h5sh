# -*- coding: utf-8 -*-

"""Functions for navigating an HDF5 file."""


from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
from h5sh.utils import (make_column_kv_fmt, short_describe, subgroup)

from .base import Command
from .registry import register

import h5py
###############################################################################


class Chdir(Command):
    name = "cd"

    def build_parser(self):
        parser = super(Chdir, self).build_parser(
            description="Change the current HDF5 group.")
        parser.add_argument('group', nargs='?')
        return parser

    def execute(self, state, group=None):
        try:
            state.chdir(group)
        except KeyError as e:
            raise ValueError(str(e))


cd = register.instance(Chdir)


@register("Print the path to the current HDF5 group")
def pwd(state):
    print(state.cwd)


class Up(object):
    def __init__(self, count):
        self.name = "u" + "p" * count
        self.path = "../" * count
        self.description = "Traverse up {:d} directories.".format(count)

    def __call__(self, state):
        cd(state, self.path)


for _i in range(1, 6):
    register.instance(Up, _i)
del _i


class Listdir(Command):
    name = "ls"

    def build_parser(self):
        parser = super(Listdir, self).build_parser(
            description="List items in the current group.")
        parser.add_argument('-l', dest='long', action='store_true',
                            help="Print attributes as well as names")
        parser.add_argument('-1', dest='oneline', action='store_true',
                            help="Print one entry per line")
        parser.add_argument('group', nargs='?')
        return parser

    def execute(self, state, long, oneline, group=None):
        if group is not None:
            group = subgroup(state.group, group)
        else:
            group = state.group

        keys = sorted(group)
        if not keys:
            return

        if long:
            fmt = make_column_kv_fmt(keys)
            for k in keys:
                v = group.get(k, getlink=True)
                if isinstance(v, h5py.HardLink):
                    v = group[k]
                v = short_describe(v)
                print(fmt(k, v))
        elif oneline:
            for k in keys:
                print(k)
        else:
            print(" ".join(keys))


ls = register.instance(Listdir)


@register("Alias for 'ls -l'")
def l(state, *args):
    ls(state, "-l", *args)
