# -*- coding: utf-8 -*-

"""Command-line utilities subsystem."""

# Command utilities
from .base import Command
from .miniargparse import MiniArgParser
from .registry import COMMANDS, register

# Load actual commands
from . import navigation
from . import query
from . import system

