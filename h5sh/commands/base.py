# -*- coding: utf-8 -*-

"""Registry of available commands."""

from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
from .miniargparse import MiniArgParser, MiniSystemExit

class Command(object):
    """Utility class for constructing a command that takes arguments.
    """
    name = None

    def __init__(self):
        self.parser = self.build_parser()

    def build_parser(self, **kwargs):
        parser = MiniArgParser(prog=self.name, **kwargs)
        return parser

    def execute(self, state, *args, **kwargs):
        raise NotImplementedError()

    def __call__(self, state, *args):
        # Parse the arguments
        try:
            parsed = self.parser.parse_args(args)
        except MiniSystemExit:
            return

        self.execute(state, **vars(parsed))

    def get_completions(self, document, args, state):
        """Get completions for this command.

        'args' is the list of given arguments to the command.
        """
        in_word = document.get_word_before_cursor(WORD=True)
        if in_word.startswith('-'):
            for arg in self.parser.options:
                yield arg
        else:
            if self.parser.dataset:
                for arg in state.datasets:
                    yield arg
            if self.parser.group:
                for arg in state.subgroups:
                    yield arg

    @property
    def description(self):
        desc = self.parser.description
        if not desc:
            raise AttributeError(desc)
        return desc

