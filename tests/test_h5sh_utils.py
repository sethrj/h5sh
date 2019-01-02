#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (division, absolute_import, print_function, )

from pprint import pprint
import pytest
import h5py
import sys

import h5sh.utils as module

@pytest.mark.skipif(sys.version_info < (3,3),
        reason="Test is for Python 3 only (unicode support")
def test_format_shape():
    format_shape = module.format_shape
    assert "scalar" == format_shape(())
    assert "2" == format_shape((2,))
    assert "2×10" == format_shape((2,10))
    assert "2×∞" == format_shape((2,None))

def test_shlex_split():
    split = module.shlex_split
    assert [] == split('')
    assert ['foo'] == split('foo')
    assert ['foo', 'bar'] == split('foo bar')
    assert ['foo bar'] == split(r'foo\ bar')
    assert ['foo bar', 'baz'] == split(r'"foo bar" baz')
    assert ['foo bar', 'baz'] == split(r'"foo bar" "baz')

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
        with pytest.raises(ValueError):
            subgroup(example_h5_file, 'nonexist')

def test_items(example_h5_filename):
    with h5py.File(example_h5_filename, 'r') as f:
        items = dict(module.items(f))
        assert sorted(items) == ['extgroup', 'extlink', 'group', 'link',
                'softlink', 'subsubgroup_hardlink']
        assert isinstance(items['group'], h5py.Group)
        assert isinstance(items['softlink'], h5py.SoftLink)
        assert isinstance(items['extgroup'], h5py.ExternalLink)
        assert isinstance(items['extlink'], h5py.ExternalLink)
        items = dict(module.items(f['group']))
        assert isinstance(items['scalar'], h5py.Dataset)

def test_short_describe(example_h5_filename):
    descr = module.short_describe
    with h5py.File(example_h5_filename, 'r') as f:
        items = dict((k,descr(v)) for (k,v) in module.items(f))
        # pprint(items)
        assert items == {
                'extgroup': 'Link (.../example-data-external.h5:external_group)',
                'extlink': 'Link (.../example-data-external.h5:external_ds)',
                'group': 'Group (3 items)',
                'link': 'Dataset (i: 3)',
                'softlink': 'Link (/group/scalar)',
                'subsubgroup_hardlink': 'Group (0 items)'}
        items = dict((k,descr(v)) for (k,v) in module.items(f['group']))
        assert items == {
                'scalar': 'Dataset (d: scalar)',
                'subgroup': 'Group (1 item)',
                'vector': 'Dataset (i: 3)'}

def test_unescape_string():
    un = module.unescape_string
    assert "This\nis Sparta" == un(r"This\nis Spart\x61")

