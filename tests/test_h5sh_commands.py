#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from h5sh.state import State
import h5sh.commands as module
from six import PY2

@pytest.fixture
def tmpstate(example_h5_filename):
    with State(example_h5_filename) as f:
        yield f

def test_interrupt(tmpstate, capsys):
    cmd = module.system.INTERRUPT_CMD
    tmpstate = None
    cmd(tmpstate)
    assert "\n" == capsys.readouterr().out
    cmd(tmpstate)
    assert "exit" in capsys.readouterr().out

def test_exit(tmpstate, capsys):
    cmd = module.COMMANDS['exit']
    tmpstate = None
    with pytest.raises(SystemExit):
        cmd(tmpstate)

def test_cd(tmpstate, capsys):
    cmd = module.COMMANDS['cd']

    # Into a group
    cmd(tmpstate, 'group')
    assert '/group' == tmpstate.cwd
    # Into a relative path
    cmd(tmpstate, '..')
    assert '/' == tmpstate.cwd
    cmd(tmpstate)
    assert '/' == tmpstate.cwd
    with pytest.raises(ValueError):
        cmd(tmpstate, 'link')
    with pytest.raises(ValueError):
        cmd(tmpstate, 'nonexistent')

def test_up(tmpstate, capsys):
    up = module.COMMANDS['up']
    cd = module.COMMANDS['cd']

    # Into a group
    cd(tmpstate, 'group')
    up(tmpstate)
    assert '/' == tmpstate.cwd

def test_ls(tmpstate, capsys):
    cmd = module.COMMANDS['ls']
    tmpstate.chdir('group')
    cmd(tmpstate)
    assert 'scalar subgroup vector\n' == capsys.readouterr().out

    cmd(tmpstate, '-l')
    assert """\
scalar   Dataset (d: scalar)
subgroup Group (1 item)
vector   Dataset (i: 3)
""" == capsys.readouterr().out

    cmd(tmpstate, '-1')
    assert 'scalar\nsubgroup\nvector\n' == capsys.readouterr().out

    tmpstate.chdir('/')
    cmd(tmpstate, '-l')
    assert """\
extgroup             Link (.../example-data-external.h5:external_group)
extlink              Link (.../example-data-external.h5:external_ds)
group                Group (3 items)
link                 Dataset (i: 3)
softlink             Link (/group/scalar)
subsubgroup_hardlink Group (0 items)
""" == capsys.readouterr().out

def test_dump(tmpstate, capsys, tmpdir):
    cmd = module.COMMANDS['dump']

    with pytest.raises(ValueError):
        cmd(tmpstate, 'group')

    cmd(tmpstate, '/group/scalar')
    out = capsys.readouterr().out
    if PY2:
        out = out.replace("u'", "'")
    assert """\
Dataset: /group/scalar
Shape: scalar
Type: float64
Attributes:
{'cats': array(['Kali', 'Bustopher Jones'], dtype=object)}
---
1.23
""" == out

    cmd(tmpstate, '/group/scalar', "-A")
    out = capsys.readouterr().out
    if PY2:
        out = out.replace("u'", "'")
    assert """\
Dataset: /group/scalar
Shape: scalar
Type: float64
Attributes:
{'cats': array(['Kali', 'Bustopher Jones'], dtype=object)}
""" == out

    cmd(tmpstate, '/group/vector')
    assert """\
Dataset: /group/vector
Shape: 3
Type: int32
---
[1 2 3]
""" == capsys.readouterr().out

    cmd(tmpstate, '-o', str(tmpdir / 'h5cmd_test_vector.txt'), '/group/vector')
    cmd(tmpstate, '-o', str(tmpdir / 'h5cmd_test_scalar.txt'), '/group/scalar')

def test_attr(tmpstate, capsys):
    cmd = module.COMMANDS['attr']

    cmd(tmpstate)
    assert "" == capsys.readouterr().out

def test_help(tmpstate, capsys):
    cmd = module.COMMANDS['help']
    tmpstate = None
    cmd(tmpstate)
    s = capsys.readouterr().out
    assert s.startswith("Available commands:")

