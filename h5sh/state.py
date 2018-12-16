# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function,
        unicode_literals)
#-----------------------------------------------------------------------------#
from contextlib import contextmanager
import h5py
import os
import sys

from .utils import abspath
from .styles import (styled_filename, HDF5_GROUP, PROMPT_TOKEN)

###############################################################################

class State(object):
    """The state of the current "shell".

    At the moment this merely encapsulates the working directory and the open
    file.
    """

    def __init__(self, filename, mode='r'):
        # HDF5 file
        self.f = h5py.File(filename, mode)
        # Current group
        self.group = self.f
        # Groups/datasets inside the current group
        self._cur_items = None

    @property
    def subgroups(self):
        """Get a cached list of groups inside the current group.
        """
        if self._cur_items is None:
            self._update_cur_items()
        return self._cur_items[0]

    @property
    def datasets(self):
        """Get a cached list of datasets inside the current group.
        """
        if self._cur_items is None:
            self._update_cur_items()
        return self._cur_items[1]

    def _update_cur_items(self):
        _cur_group = self.group
        groups = []
        datasets = []
        for key in _cur_group:
            cls = _cur_group.get(key, getclass=True)
            if issubclass(cls, h5py.Group):
                groups.append(key)
            elif issubclass(cls, h5py.Dataset):
                datasets.append(key)
        self._cur_items = (groups, datasets)

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
        # Clear cache of current items
        self._cur_items = None

    @property
    def filename(self):
        """Filename of the file"""
        return self.f.filename

    @property
    def cwd(self):
        """Path of the current HDF5 group"""
        return self.group.name

    def get_styled_prompt(self, output):
        """Get a list [(clsfmt, text), ...] for the prompt.
        """
        cols = output.get_size().columns
        cwd = self.cwd
        # Try to fit the prompt on no more than half the terminal width
        max_filename_len = cols // 2 - (len(cwd) + 4)

        result = styled_filename(self.filename, max_filename_len) + [
                ('', ":"),
                (HDF5_GROUP, self.cwd),
                (PROMPT_TOKEN, ' > '),
                ]

        return result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

###############################################################################
# end of Nemesis/python/exnihilotools/h5sh/state.py
###############################################################################
