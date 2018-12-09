#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
from contextlib import contextmanager
import numpy as np
import h5py

import unittest as unittest
#from exnihilotools.files import stdout_string
###############################################################################
from h5sh.state import State
import h5sh.commands as module

#FILENAME = unittest.test_data_path("Nemesis/python", "example-data.h5")

class TestCommands(unittest.TestCase):

    @contextmanager
    def make_state(self):
        with State(FILENAME) as f:
            yield f

    def test_interrupt(self):
        cmd = module.INTERRUPT_CMD
        state = None
        with stdout_string() as get_string:
            cmd(state)
            self.assertEqual("\n", get_string())
            cmd(state)
            self.assertTrue("exit" in get_string())

    def test_exit(self):
        cmd = module.COMMANDS['exit']
        state = None
        self.assertRaises(SystemExit, cmd, state)

    def test_cd(self):
        cmd = module.COMMANDS['cd']
        with self.make_state() as state:
            # Into a group
            cmd(state, 'group')
            self.assertEqual('/group', state.cwd)
            # Into a relative path
            cmd(state, '..')
            self.assertEqual('/', state.cwd)
            cmd(state)
            self.assertEqual('/', state.cwd)
            self.assertRaises(ValueError, cmd, state, 'link')
            self.assertRaises(ValueError, cmd, state, 'nonexistent')


    def test_up(self):
        up = module.COMMANDS['up']
        cd = module.COMMANDS['cd']
        with self.make_state() as state:
            # Into a group
            cd(state, 'group')
            up(state)
            self.assertEqual('/', state.cwd)

    def test_ls(self):
        cmd = module.COMMANDS['ls']
        with self.make_state() as state:
            state.chdir('group')
            with stdout_string() as get_string:
                cmd(state)
                self.assertEqual('scalar subgroup vector\n', get_string())
            with stdout_string() as get_string:
                cmd(state, '-l')
                self.assertEqual("""\
scalar   Dataset (d: scalar)
subgroup Group (1 items)
vector   Dataset (i: 3)
""", get_string())
            with stdout_string() as get_string:
                cmd(state, '-1')
                self.assertEqual('scalar\nsubgroup\nvector\n', get_string())
            state.chdir('/')
            with stdout_string() as get_string:
                cmd(state, '-l')
                self.assertEqual("""\
extgroup             Group (0 items)
extlink              Dataset (d: 4)
group                Group (3 items)
link                 Dataset (i: 3)
softlink             Dataset (d: scalar)
subsubgroup_hardlink Group (0 items)
""", get_string())

    def test_dump(self):
        cmd = module.COMMANDS['dump']
        with self.make_state() as state:
            self.assertRaises(ValueError, cmd, state, 'group')
            with stdout_string() as get_string:
                cmd(state, '/group/scalar')
                self.assertEqual("""\
/group/scalar: scalar
Type         : float64
Attributes   : {'cats': array(['Kali', 'Bustopher Jones'], dtype=object)}
1.23
""", get_string().replace("u'","'"))

            with stdout_string() as get_string:
                cmd(state, '/group/scalar', "-A")
                self.assertEqual("""\
/group/scalar: scalar
Type         : float64
Attributes   : {'cats': array(['Kali', 'Bustopher Jones'], dtype=object)}
""", get_string().replace("u'","'"))

            with stdout_string() as get_string:
                cmd(state, '/group/vector')
                self.assertEqual("""\
/group/vector: 3
Type         : int32
[1 2 3]
""", get_string())

            cmd(state, '-o', 'h5cmd_test_vector.txt', '/group/vector')
            cmd(state, '-o', 'h5cmd_test_scalar.txt', '/group/scalar')

    def test_attr(self):
        cmd = module.COMMANDS['attr']
        with self.make_state() as state:
            with stdout_string() as get_string:
                cmd(state)
                self.assertEqual("", get_string())

    def test_help(self):
        cmd = module.COMMANDS['help']
        state = None
        with stdout_string() as get_string:
            cmd(state)
            s = get_string()
            self.assertTrue(s.startswith("Available commands:"))
        #print(repr(s))

    def test_prompt(self):
        cmd = module.COMMANDS['prompt']
        with self.make_state() as state:
            cmd(state, "{s.basename}:{s.cwd}")
            with stdout_string() as get_string:
                cmd(state)
                self.assertEqual("'{s.basename}:{s.cwd}'\n", get_string())
            self.assertEqual("example-data.h5:/", state.get_prompt())


#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    unittest.main()

