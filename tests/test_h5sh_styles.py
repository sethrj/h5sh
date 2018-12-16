#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (division, absolute_import, print_function,
        unicode_literals)

from pprint import pprint
import pytest
import h5py

import h5sh.styles as module

def test_styled_filename():
    style = module.styled_filename
    FN = module.FILENAME
    TFN = module.TRUNC_FILENAME

    assert style("foo.h5") == [(FN, 'foo.h5')]
    assert style("abcd"*8 + ".h5") == [
            (FN, 'abcdabcdabcd'), (TFN, '...'), (FN, 'dabcdabcd.h5')]
    assert style("x"*32 + "/foo.h5") == [
            (TFN, '.../'), (FN, 'foo.h5')]
    assert style("x"*32 + "/" + "abcd"*8 + ".h5") == [
            (TFN, '.../'), (FN, 'abcdabcdabcd'), (TFN, '...'),
            (FN, 'dabcdabcd.h5')]
    assert style("basename/" + "abcd"*8 + ".h5") == [
            (TFN, '.../'), (FN, 'abcdabcdabcd'), (TFN, '...'),
            (FN, 'dabcdabcd.h5')]

