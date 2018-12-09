# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
from contextlib import contextmanager
import h5py
import os
import sys

from .utils import abspath, readline, IS_READLINE_LIBEDIT
###############################################################################


def _get_default_color_prompt():
    from exnihilotools.terminal import (ansi_color as ansi, COLORS,
                                        RESET_STYLE)
    return "".join([ansi(COLORS['fb']), "{s.basename}",
                    ansi(RESET_STYLE), ":", ansi(COLORS['fg']), "{s.cwd}",
                    ansi(RESET_STYLE), "> "])


class State(object):
    """The state of the current "shell".

    At the moment this merely encapsulates the working directory and the open
    file.
    """

    def __init__(self, filename, mode='r'):
        # Path to the file
        self.basename = os.path.basename(filename)
        # HDF5 file
        self.f = h5py.File(filename, mode)
        # Current group
        self.group = self.f
        #: Prompt
        prompt = "> "
        if sys.stdout.isatty():
            if not IS_READLINE_LIBEDIT:
                prompt = _get_default_color_prompt()
            else:
                # Libedit (and/or the python interface to it) conspire to write
                # ASCII terminal sequences as literal characters, so colors
                # don't work properly.
                prompt = "{s.basename}: {s.cwd}> "
        self.prompt = prompt.format

    def close(self):
        self.f.close()
        self.f = None

    @property
    def closed(self):
        return self.f is None

    def chdir(self, dir=None):
        if dir is None:
            # Return to base directory
            self.group = self.f
            return

        if '.' in dir:
            dir = abspath(dir, self.cwd)

        group = self.group[dir]
        if not isinstance(group, h5py.Group):
            raise ValueError("{} is not a group".format(group.name))
        self.group = group

    @property
    def filename(self):
        """Filename of the file"""
        return self.f.filename

    @property
    def cwd(self):
        """Path of the current HDF5 group"""
        return self.group.name

    def get_prompt(self):
        """Get the prompt given our current state.
        """
        return self.prompt(s=self)

    def __eq__(self, other):
        return self.group == other.group and self.prompt == other.prompt

    def __ne__(self, other):
        return not (self == other)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

###############################################################################
# end of Nemesis/python/exnihilotools/h5sh/state.py
###############################################################################
