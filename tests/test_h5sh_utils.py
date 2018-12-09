#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (division, absolute_import, print_function, )

import pytest
import h5py

import h5sh.utils as module

def test_abspath():
    abspath = module.abspath

    assert "/foo/bar" == abspath("bar",   "/foo")
    assert "/" == abspath("/", "/foo")
    assert "/" == abspath("//////", "/foo")
    assert "/bar" == abspath("////bar", "/foo")
    assert "/bar" == abspath("bar",   "/")
    assert "/foo" == abspath("./foo", "/")
    assert "/foo" == abspath("./foo/", "/")
    assert "/foo" == abspath(".", "/foo")
    assert "/foo/bar" == abspath("..", "/foo/bar/baz")
    assert "/foo" == abspath("..", "/foo/bar")
    assert "/" == abspath("..", "/group")
    assert "/" == abspath("../..", "/foo/bar")
    assert "/foo" == abspath("../..", "/foo/bar/baz")
    assert "/foo" == abspath("/foo", "/bar/baz")

def test_subgroup(example_h5_filename):
    subgroup = module.subgroup
    with h5py.File(example_h5_filename, 'r') as example_h5_file:
        g = subgroup(example_h5_file, 'group')
        assert '/group' == g.name
        assert '/group' == subgroup(g, '.').name
        assert '/' == subgroup(g, '..').name
        assert '/group/subgroup' == subgroup(g, 'subgroup').name
        assert '/external_group' == subgroup(g, '/extgroup').name
        assert ('/subsubgroup_hardlink'
                == subgroup(g, '../subsubgroup_hardlink').name)
        with pytest.raises(ValueError):
            subgroup(example_h5_file, 'extlink')
        with pytest.raises(KeyError):
            subgroup(example_h5_file, 'nonexist')

def test_unescape_string():
    un = module.unescape_string
    assert "This\nis Sparta" == un(r"This\nis Spart\x61")

