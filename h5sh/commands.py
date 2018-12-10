# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
from argparse import ArgumentParser
from pprint import pformat
import sys
from time import time

from numpy import printoptions
from .utils import (short_describe, make_column_kv_fmt, to_native_str, extract,
                    readline, unescape_string, np, subgroup, format_shape)
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

###############################################################################
# COMMAND LIST
###############################################################################


class CommandList(object):
    def __init__(self, commands=None):
        if commands is None:
            commands = {}
        self.commands = commands

    def __repr__(self):
        return "CommandList({!r})".format(self.commands)

    def insert(self, key, func):
        if key in self.commands:
            raise KeyError("Duplicate command name '{}'".format(key))
        self.commands[key] = func

    def __iter__(self):
        return iter(self.commands)

    def __getitem__(self, key):
        return self.commands[key]


# List of commands
COMMANDS = CommandList()


def add_named_command(name):
    """Decorator to add a command with a special name.
    """
    def func(f, name=name):
        COMMANDS.insert(name, f)
        return f

    return func


def add_command(f):
    """Decorator to add a command from a function.
    """
    COMMANDS.insert(f.__name__, f)
    return f

###############################################################################


class CommandCompleter(object):
    """Readline completion for top-level commands.
    """

    def __init__(self, state):
        # Accessor to the console state
        self.state = state

        # Persistent data
        self.cmds = sorted(COMMANDS)

        # Iterator/generator for the current candidates
        self.candidates = None

    def __call__(self, text, idx):
        if not idx:
            # First call to complete with the current text
            self.init(text)

        try:
            response = next(self.candidates)
        except StopIteration:
            # Last autocomplete value reached; reset
            response = None
            self.candidates = None

        return response

    def init(self, text):
        (beg, end) = (readline.get_begidx(), readline.get_endidx())
        line = readline.get_line_buffer().rstrip('\n')

        # Text being completed
        ctext = line[beg:end]
        if not ctext:
            # Loop through available commands
            self.candidates = (c for c in self.cmds
                               if not c.startswith('__'))
            return

        self.candidates = (c for c in self.cmds if c.startswith(ctext))

###############################################################################
# COMMAND CLASS
###############################################################################


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

    @property
    def description(self):
        desc = self.parser.description
        if not desc:
            raise AttributeError(desc)
        return desc


def add_command_instance(cls, *args, **kwargs):
    """Decorator to add a command from a function.
    """
    global COMMANDS
    instance = cls(*args, **kwargs)
    COMMANDS.insert(instance.name, instance)
    return instance

###############################################################################
# COMMANDS
###############################################################################


class Interrupt(object):
    name = "__INTERRUPT__"
    warning_time = 2

    def __init__(self):
        self.last_time = 0

    def __call__(self, state):
        cur_time = time()
        if cur_time - self.last_time < Interrupt.warning_time:
            # Print helpful message on two consecutive interrupts within 2
            # seconds
            print("\n(Use the 'exit' command or type Ctrl-D to quit)")
        else:
            print()
        self.last_time = cur_time


INTERRUPT_CMD = add_command_instance(Interrupt)

###############################################################################


@add_named_command("__NULL__")
def null(state):
    pass


NULL_CMD = null

###############################################################################


@add_named_command("exit")
def _exit(state):
    sys.exit(0)


_exit.description = "Exit h5sh"

###############################################################################


@add_command
def cd(state, subdir=None):
    try:
        state.chdir(subdir)
    except KeyError as e:
        raise ValueError(str(e))


cd.description = "Change the current HDF5 group"


@add_command
def pwd(state):
    print(state.cwd)


pwd.description = "Print the path to the current HDF5 group"


class Up(object):
    def __init__(self, count):
        self.name = "u" + "p" * count
        self.path = "../" * count
        self.description = "Traverse up {:d} directories".format(count)

    def __call__(self, state):
        cd(state, self.path)


for _i in range(1, 6):
    add_command_instance(Up, _i)
del _i

###############################################################################


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


ls = add_command_instance(Listdir)


@add_command
def l(state, *args):
    ls(state, "-l", *args)


l.description = "Alias for 'ls -l'"

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
            with printoptions(**kwargs):
                print(item, file=f)
        else:
            print(item, file=f)


add_command_instance(Dump)

###############################################################################


class Attrs(Command):
    name = "attr"

    def build_parser(self):
        parser = MiniArgParser(
            prog=self.name,
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


add_command_instance(Attrs)

###############################################################################


@add_named_command("help")
def _help(state):
    print("Available commands:")
    keys = sorted(k for k in COMMANDS if not k.startswith("__"))
    fmt = make_column_kv_fmt(keys, " - ")
    for k in keys:
        cmd = COMMANDS[k]
        try:
            desc = cmd.description
        except AttributeError:
            desc = ""

        print(fmt(k, desc))


_help.description = "List available commands"

###############################################################################


@add_command
def filename(state):
    print(state.f.filename)


filename.description = "Print the name of the file being examined"

###############################################################################


@add_command
def prompt(state, text=None):
    if text is None:
        # Print the prompt if no argument is specified
        print(repr(state.prompt.__self__))
        return

    try:
        text = unescape_string(text)
    except Exception as e:
        raise ValueError("Couldn't process prompt string:" + str(e))

    new_prompt = text.format

    # Shlex escapes the escape characters if user embeds in quotes.
    try:
        new_prompt(s=state)
    except Exception as e:
        raise ValueError("Couldn't set prompt:" + str(e))

    state.prompt = new_prompt


prompt.description = "Get or change the terminal prompt"

