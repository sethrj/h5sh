# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function, )
from six.moves import input
#-----------------------------------------------------------------------------#
import os
import shlex
import sys
import warnings

from .commands import COMMANDS, INTERRUPT_CMD, NULL_CMD, CommandCompleter
from .utils import readline, IS_READLINE_LIBEDIT
###############################################################################

HISTFILE = os.path.expanduser('~/.h5sh_history')
COMPLETER = None

#pylint: disable=function-redefined


def setup_readline(state):
    """Initialize the readline completer and init file.

    After executing, this function replaces itself with a null-op.
    """
    global setup_readline, COMPLETER

    def setup_readline(s): return None

    if not readline:
        # Readline module could not be imported
        warnings.warn("Command line completion unavailable: `readline` "
                      "could not be imported", RuntimeWarning)
        return

    # Set up input configuration
    try:
        readline.read_init_file(os.path.expanduser('~/.inputrc'))
    except IOError:
        pass

    # Create completer
    COMPLETER = CommandCompleter(state)

    # Set up tab completion
    readline.set_completer(COMPLETER)
    if not IS_READLINE_LIBEDIT:
        # Actual GNU readline
        readline.parse_and_bind("tab: complete")
    else:
        # Mac OS X readline emulator
        readline.parse_and_bind("bind ^I rl_complete")

    # Set up history file
    try:
        readline.read_history_file(HISTFILE)
    except IOError:
        pass

    import atexit
    atexit.register(lambda: readline.write_history_file(HISTFILE))


class Console(object):
    def __init__(self, state):
        self.state = state
        # Debug mode
        self.debug = False

        # Set up readline
        global setup_readline
        setup_readline(self.state)

    def read(self):
        """Prompt for and read a single command.
        """
        try:
            text = input(self.state.get_prompt())
        except KeyboardInterrupt:
            cmd = INTERRUPT_CMD.name
            args = ()
        except EOFError:
            cmd = "exit"
            args = ()
        else:
            args = shlex.split(text)
            if args:
                cmd = args[0]
                args = args[1:]
            else:
                (cmd, args) = ("__NULL__", ())
        return (cmd, args)

    def interact(self):
        while True:
            (cmd_name, args) = self.read()
            try:
                cmd = COMMANDS[cmd_name]
            except KeyError:
                print("h5sh: {}: command not found".format(cmd_name))
                continue

            try:
                cmd(self.state, *args)
            except KeyboardInterrupt:
                INTERRUPT_CMD(self.state)
            except Exception as e:
                if self.debug:
                    import logging as log
                    log.exception(e)
                    raise
                if isinstance(e, (TypeError, ValueError)):
                    print("{}: {!s}".format(cmd_name, e))
                    continue

