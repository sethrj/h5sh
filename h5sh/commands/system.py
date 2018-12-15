# -*- coding: utf-8 -*-

"""h5sh system utility functions."""

from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
import sys
from time import time

from h5sh.utils import (make_column_kv_fmt, short_describe, unescape_string)

from .base import Command
from .registry import register, COMMANDS
###############################################################################

class Interrupt(object):
    name = "__INTERRUPT__"
    warning_time = 2.0

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


INTERRUPT_CMD = register.instance(Interrupt)

###############################################################################

@register(name="__NULL__")
def null(state):
    pass

NULL_CMD = null

###############################################################################

@register(name="exit", description="Exit h5sh")
def _exit(state):
    sys.exit(0)

###############################################################################

@register(name='help',
          description="List available commands")
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

###############################################################################

@register("Print the name of the file being examined")
def filename(state):
    print(state.f.filename)

###############################################################################

@register("Get or change the terminal prompt")
def prompt(state, text=None):
    if text is None:
        # Print the prompt if no argument is specified
        print(repr(state.prompt.__self__))
        return

    try:
        text = unescape_string(text)
    except Exception as e:
        raise ValueError("Couldn't process prompt string: " + str(e))

    new_prompt = text.format

    # Shlex escapes the escape characters if user embeds in quotes.
    try:
        new_prompt(s=state)
    except Exception as e:
        raise ValueError("Couldn't set prompt: " + str(e))

    state.prompt = new_prompt

