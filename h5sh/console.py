# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function,
        unicode_literals)
from six.moves import input
#-----------------------------------------------------------------------------#
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style

from .commands import COMMANDS
from .commands.system import INTERRUPT_CMD, NULL_CMD
from .styles import get_style_rules
from .utils import shlex_split

###############################################################################

def _get_console_lexer():
    try:
        from prompt_toolkit.lexers import PygmentsLexer
        from pygments.lexers import BashLexer
    except ImportError:
        return None
    return PygmentsLexer(BashLexer)

class CommandCompleter(Completer):
    def __init__(self, state):
        self.state = state
        self.cmd_names = sorted(k for k in COMMANDS if not k.startswith('_'))

    def get_completions(self, document, complete_event):
        preceding_word = document.get_word_before_cursor(WORD=True)

        if len(document.text) == len(preceding_word):
            # Empty or completing the first command: list commands that start
            # with the prefix
            completions = self.cmd_names
        else:
            # Process the text that's there
            args = shlex_split(document.text)
            try:
                cmd = COMMANDS[args[0]]
            except KeyError:
                return

            try:
                get_completions = cmd.get_completions
            except AttributeError:
                return

            completions = cmd.get_completions(document, args[1:], self.state)

        pos = -len(preceding_word)
        for arg in completions:
            if arg.startswith(preceding_word):
                yield Completion(arg, pos)

class Console(object):
    def __init__(self, state):
        # Command-line state
        self.state = state
        # Debug mode
        self.debug = False
        # Prompt session
        self.session = PromptSession(lexer=_get_console_lexer(),
                style=Style(get_style_rules()),
                completer=CommandCompleter(state))
        # prompt_toolkit Output class
        self.output = self.session.app.output

    def prompt(self):
        with patch_stdout(raw=True):
            prompt = FormattedText(self.state.get_styled_prompt(self.output))
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
            args = shlex_split(text)
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

