# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function,
        unicode_literals)
#-----------------------------------------------------------------------------#
import os

FILENAME = 'class:filename'
TRUNC_FILENAME = 'class:filename.trunc'
HDF5_GROUP = 'class:hdf5.group'
PROMPT_TOKEN = 'class:prompt'

STYLES = [
        (FILENAME, 'fg:cyan'),
        (TRUNC_FILENAME, 'fg:gray'),
        (HDF5_GROUP, 'fg:green'),
        (PROMPT_TOKEN, 'bold'),
        ]

def get_style_rules():
    return [(k.replace('class:',''), v) for (k,v) in STYLES]

def styled_filename(filename, width=32):
    """Filename, truncated to the given width, as a list to be wrapped by
    prompt_toolkit.FormattedText.
    """
    def len_le_width(result):
        return sum(len(v[1]) for v in result) <= width

    result = [(FILENAME, filename)]
    if len_le_width(result):
        # If the full path is small, just return it
        return result

    # See if we can strip the leading directories
    basename = os.path.basename(filename)
    if basename != filename:
        # Shortened the directory
        dirname = [(TRUNC_FILENAME, ".../")]
        result = dirname + [(FILENAME, basename)]
    else:
        dirname = []

    if len_le_width(result):
        # If the full path is small, just return it
        return result

    # Length for half of basename, subtracting len('.../') + len('...')
    half_width = (width - 7) // 2
    result = dirname + [
              (FILENAME, basename[:half_width]),
              (TRUNC_FILENAME, "..."),
              (FILENAME, basename[-half_width:])]
    return result

