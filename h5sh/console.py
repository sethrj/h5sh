# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function,
        unicode_literals)
from six.moves import input
#-----------------------------------------------------------------------------#
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style
import shlex

from .commands import COMMANDS
from .commands.system import INTERRUPT_CMD, NULL_CMD
from .styles import get_style_rules

###############################################################################

def _get_console_lexer():
    try:
        from prompt_toolkit.lexers import PygmentsLexer
        from pygments.lexers import BashLexer
    except ImportError:
        return None
    return PygmentsLexer(BashLexer)

class Console(object):
    def __init__(self, state):
        # Command-line state
        self.state = state
        # Prompt session
        self.session = PromptSession(lexer=_get_console_lexer(),
                style=Style(get_style_rules()))
        # Debug mode
        self.debug = False

    def prompt(self):
        with patch_stdout(raw=True):
            prompt = FormattedText(self.state.get_styled_prompt())
            text = self.session.prompt(prompt)
        return text

    def read(self):
        """Prompt for and read a single command.
        """
        try:
            text = self.prompt()
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

