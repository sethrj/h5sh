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

