# -*- coding: utf-8 -*-

"""Registry of available commands."""

from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
import sys
from functools import wraps

DEFINE_PARSER = ('argparse' in sys.modules)


class CommandRegistry(object):
    def __init__(self, commands=None):
        if commands is None:
            commands = {}
        self.commands = commands

    def __repr__(self):
        return "CommandRegistry({!r})".format(self.commands)

    def insert(self, key, func):
        if key in self.commands:
            raise KeyError("Duplicate command name '{}'".format(key))

        if DEFINE_PARSER:
            try:
                parser = func.parser
            except AttributeError:
                pass
            else:
                self._add_parser_cmd(key, parser)

        self.commands[key] = func

    def _add_parser_cmd(self, name, parser):
        """Define a free function that returns a function's parser.

        This is used by the 'sphinx-argparse' documentation generator.
        """
        module = sys.modules[__name__]
        attrname = "get_parser_" + name
        setattr(module, attrname, lambda: parser)

    def __iter__(self):
        return iter(self.commands)

    def __getitem__(self, key):
        return self.commands[key]


class RegisterCommand(object):
    def __init__(self, registry):
        self.registry = registry

    def __call__(self, description=None, name=None):
        """Add the following function using the function name as the command
        name.

        Example::

            @register(description="Print the current directory")
            def pwd(state):
                print(state.cwd)

        """
        def func(f, registry=self.registry, name=name, description=description):
            if name is None:
                name = f.__name__
            if description is not None:
                f.description = description
            registry.insert(name, f)
            return f

        return func

    def instance(self, cls, *args, **kwargs):
        """Add an *instance* of the given class to the command registry.

        Example::

            INTERRUPT_CMD = register.instance(Interrupt)

        """
        instance = cls(*args, **kwargs)
        self.registry.insert(instance.name, instance)
        return instance


# List of commands
COMMANDS = CommandRegistry()

# Register in the list of commands
register = RegisterCommand(COMMANDS)
