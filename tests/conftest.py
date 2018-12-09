#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import h5py
import numpy as np

@pytest.fixture
def example_h5_filename(tmpdir, scope='module'):
    ext_filename = (tmpdir / "example-data-external.h5")
    filename = (tmpdir / "example-data.h5")

    with h5py.File(ext_filename,'w') as f:
        d = f.create_dataset("external_ds", data=np.array([1,2,3,4], dtype='d'))
        g = f.create_group("external_group")

    with h5py.File(filename,'w') as f:
        g = f.create_group("group")
        g.attrs['unit'] = "Flerbians"
        g.attrs['count'] = 123
        g2 = g.create_group("subgroup")
        g3 = g2.create_group("subsubgroup")

        d1 = g.create_dataset("scalar", data=1.23)
        d1.attrs['cats'] = np.array(["Kali", "Bustopher Jones"],
                                     dtype=h5py.special_dtype(vlen=str))

        d2 = g.create_dataset("vector", data=np.array([1,2,3], dtype='i'))
        f['link'] = d2
        f['softlink'] = h5py.SoftLink('/group/scalar')
        f['subsubgroup_hardlink'] = g3
        f['extlink'] = h5py.ExternalLink(ext_filename, "external_ds")
        f['extgroup'] = h5py.ExternalLink(ext_filename, "external_group")

    yield filename
