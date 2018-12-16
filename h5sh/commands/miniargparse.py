# -*- coding: utf-8 -*-

"""Argument parser."""

from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
from argparse import ArgumentParser
###############################################################################

class MiniSystemExit(BaseException):
    pass

class MiniArgParser(ArgumentParser):
    """Argument parser that just returns/raises instead of exiting.

    This utility class is used to parse arguments without actually exiting the
    python shell.
    """
    def __init__(self, *args, **kwargs):
        self.options = []
        self.dataset = False
        self.group = False
        super(MiniArgParser, self).__init__(*args, **kwargs)

    def exit(self, status=0, message=None):
        """Instead of calling sys.exit, raise an appropriate exception.
        """
        if status:
            raise TypeError(message)

        # If exit successful, just print the message
        raise MiniSystemExit(message)

    def error(self, message):
        """Instead of calling sys.exit, raise a type error.
        """
        raise TypeError(message)

    def add_dataset_argument(self, *args, **kwargs):
        self.dataset = True
        return super(MiniArgParser, self).add_argument('dataset',
                *args, **kwargs)

    def add_group_argument(self, *args, **kwargs):
        self.group = True
        return super(MiniArgParser, self).add_argument('group',
                *args, **kwargs)

    def add_object_argument(self, *args, **kwargs):
        self.dataset = True
        self.group = True
        return super(MiniArgParser, self).add_argument('obj',
                metavar='object', *args, **kwargs)

    def add_argument(self, name, *args, **kwargs):
        if name == 'dataset':
            return self.add_dataset_argument(*args, **kwargs)
        elif name == 'group':
            return self.add_group_argument(*args, **kwargs)
        elif name == 'object':
            return self.add_object_argument(*args, **kwargs)
        args = (name,) + args
        self.options.extend(opt for opt in args if opt.startswith('-'))
        return super(MiniArgParser, self).add_argument(*args, **kwargs)

