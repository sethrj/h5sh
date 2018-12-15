# -*- coding: utf-8 -*-

"""Functions for navigating an HDF5 file."""


from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
from h5sh.utils import (make_column_kv_fmt, short_describe, subgroup)

from .base import Command
from .registry import register
###############################################################################


@register("Change the current HDF5 group")
def cd(state, subdir=None):
    try:
        state.chdir(subdir)
    except KeyError as e:
        raise ValueError(str(e))

@register("Print the path to the current HDF5 group")
def pwd(state):
    print(state.cwd)

class Up(object):
    def __init__(self, count):
        self.name = "u" + "p" * count
        self.path = "../" * count
        self.description = "Traverse up {:d} directories".format(count)

    def __call__(self, state):
        cd(state, self.path)

for _i in range(1, 6):
    register.instance(Up, _i)
del _i

class Listdir(Command):
    name = "ls"

    def build_parser(self):
        parser = super(Listdir, self).build_parser(
            description="List items in the current group")
        parser.add_argument('-l', dest='long', action='store_true')
        parser.add_argument('-1', dest='oneline', action='store_true')
        parser.add_argument('subdir', nargs='?')
        return parser

    def execute(self, state, long, oneline, subdir=None):
        group = state.group
        if subdir is not None:
            group = subgroup(group, subdir)

        keys = sorted(group)
        if not keys:
            return

        if long:
            fmt = make_column_kv_fmt(keys)
            for k in keys:
                v = short_describe(group[k])
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


