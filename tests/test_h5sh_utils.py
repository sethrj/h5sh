###############################################################################
# File  : Nemesis/python/test/test_h5sh_utils.py
# Author: Seth R Johnson
# Date  : Fri Jun 02 11:34:02 2017
###############################################################################
from __future__ import (division, absolute_import, print_function, )
#-----------------------------------------------------------------------------#
import exnihilotools.unittest as unittest

import numpy as np
import h5py
###############################################################################
import exnihilotools.h5sh.utils as module

FILENAME = unittest.test_data_path("Nemesis/python", "example-data.h5")
TEST_FILE = h5py.File(FILENAME, 'r')

class TestUtils(unittest.TestCase):
    def test_abspath(self):
        abspath = module.abspath

        self.assertEqual("/foo/bar", abspath("bar",   "/foo"))
        self.assertEqual("/", abspath("/", "/foo"))
        self.assertEqual("/", abspath("//////", "/foo"))
        self.assertEqual("/bar", abspath("////bar", "/foo"))
        self.assertEqual("/bar", abspath("bar",   "/"))
        self.assertEqual("/foo", abspath("./foo", "/"))
        self.assertEqual("/foo", abspath("./foo/", "/"))
        self.assertEqual("/foo", abspath(".", "/foo"))
        self.assertEqual("/foo/bar", abspath("..", "/foo/bar/baz"))
        self.assertEqual("/foo", abspath("..", "/foo/bar"))
        self.assertEqual("/", abspath("..", "/group"))
        self.assertEqual("/", abspath("../..", "/foo/bar"))
        self.assertEqual("/foo", abspath("../..", "/foo/bar/baz"))
        self.assertEqual("/foo", abspath("/foo", "/bar/baz"))

    def test_subgroup(self):
        subgroup = module.subgroup
        g = subgroup(TEST_FILE, 'group')
        self.assertEqual('/group', g.name)
        self.assertEqual('/group', subgroup(g, '.').name)
        self.assertEqual('/', subgroup(g, '..').name)
        self.assertEqual('/group/subgroup', subgroup(g, 'subgroup').name)
        self.assertEqual('/external_group', subgroup(g, '/extgroup').name)
        self.assertEqual('/subsubgroup_hardlink',
                subgroup(g, '../subsubgroup_hardlink').name)
        self.assertRaises(ValueError, subgroup, TEST_FILE, 'extlink')
        self.assertRaises(KeyError, subgroup, TEST_FILE, 'nonexist')

    def test_unescape_string(self):
        un = module.unescape_string
        self.assertEqual("This\nis Sparta", un(r"This\nis Spart\x61"))

#  --- TEST FILE CONTENTS ---
# /                        Group
# /extgroup                External Link {example-data-external.h5//external_group}
# /extlink                 External Link {example-data-external.h5//external_ds}
# /group                   Group
# /group/scalar            Dataset {SCALAR}
# /group/subgroup          Group
# /group/subgroup/subsubgroup Group
# /group/vector            Dataset {3}
# /link                    Dataset, same as /group/vector
# /softlink                Soft Link {/group/scalar}
# /subsubgroup_hardlink    Group, same as /group/subgroup/subsubgroup
#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    unittest.main()

###############################################################################
# end of Nemesis/python/test/test_h5sh_utils.py
###############################################################################
