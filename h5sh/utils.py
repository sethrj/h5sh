# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function, )
from six import PY3
#-----------------------------------------------------------------------------#
from exnihilotools.package import delayed_error_module

np = delayed_error_module('numpy')
h5py = delayed_error_module('h5py')
readline = delayed_error_module('readline')

# Whether the libedit compatibility version of the readline module is running
# (it has a different textual interface and capabilities)
IS_READLINE_LIBEDIT = readline and "libedit" in readline.__doc__

###############################################################################
# STRING UTILITIES
###############################################################################


def abspath(newpath, curpath):
    """Return the absolute path to the given 'newpath'.

    The current directory string must be given by 'curpath' as an absolute
    path.
    """
    assert newpath
    assert curpath
    assert curpath.startswith('/')

    subdirs = newpath.split('/')
    if not subdirs[0] or curpath == '/':
        # Absolute path (curpath is ignored)
        # or we're in the root directory
        dirs = [""]
    else:
        # Relative path; extract directory components from curpath
        dirs = curpath.split('/')

    for s in subdirs:
        if not s or s == ".":
            # Empty or 'current directory'
            pass
        elif s == "..":
            dirs.pop()
            if not dirs:
                raise ValueError("Too many '..' in path '{}'".format(newpath))
        else:
            dirs.append(s)

    if len(dirs) == 1:
        # Special case for root: joining [] or [""] return "", but you can't
        # set the first component to "/" since joining ["/","foo"] would
        # return "//foo"
        return '/'

    return '/'.join(dirs)


def subgroup(group, path):
    """Get a group inside another group, accounting for relative paths.

    This is the core functionality behind `chdir`.
    """
    assert path
    if '.' in path:
        path = abspath(path, group.name)

    try:
        group = group[path]
    except Exception as e:
        print("Failed to open group '{}' in '{}'".format(path, group.name))
        raise

    if not isinstance(group, h5py.Group):
        raise ValueError("{} is not a group (it is type {!s})".format(
            group.name, type(group).__name__))
    return group


def make_column_kv_fmt(keys, sep=" "):
    """Return the format function for a key/value pair that lines up all the
    keys and values.
    """
    maxlen = max(len(k) for k in keys) if keys else 1
    return "{{:{:d}s}}{:s}{{!s}}".format(maxlen, sep).format


if PY3:
    def unescape_string(text):
        return bytes(text, "utf-8").decode("unicode_escape")
else:
    def unescape_string(text):
        return text.decode("string_escape")

###############################################################################
# ARRAY UTILITIES
###############################################################################


def vectorized(dtype='O', nargin=1, nargout=1):
    """Decorator function for applying a python function to an array.

    Should have less overhead than ``np.vectorize``.
    """
    def _decorator(f):
        if np:
            _to_arr = np.frompyfunc(f, nargin, nargout)
        else:
            def _to_arr(x): return x

        if dtype == 'O':
            _vectorized = _to_arr
        else:
            def _vectorized(arr):
                result = _to_arr(arr)
                return np.array(result, dtype=dtype)
        return _vectorized
    return _decorator


if PY3:
    def to_native_str(s):
        if isinstance(s, bytes):
            # For ASCII-encoded attributes
            return s.decode('ascii')
        # For (possibly UTF-8 encoded attributes) or other types
        return s

    @vectorized(dtype='O')
    def to_native_str_array(s):
        return s.decode('ascii')

    @vectorized(dtype='S')
    def to_h5_str_array(s):
        return s.encode('ascii')
else:
    def to_native_str(s):
        #pylint: disable=undefined-variable
        if isinstance(s, unicode):
            return s.encode('ascii')
        # For native str datatypes or other types
        return s

    def to_native_str_array(arr):
        return arr

    def to_h5_str_array(arr):
        return arr

###############################################################################
# HDF5 UTILITIES
###############################################################################

_MULT_SYMBOL = u"\u00D7" if PY3 else "x"


def format_shape(shape):
    """Return a nicely formatted description of a dataset shape.
    """
    if not shape:
        return "scalar"
    return _MULT_SYMBOL.join(str(i) for i in shape)


def short_describe(item):
    """Return a short description of the given group/dataset.
    """
    if isinstance(item, h5py.Group):
        return "Group ({:d} items)".format(len(item))
    elif isinstance(item, h5py.Dataset):
        return "Dataset ({:s}: {:s})".format(
            item.dtype.char, format_shape(item.shape))
    elif isinstance(item, h5py.SoftLink):
        return "Link ({:s})".format(item.path)
    elif isinstance(item, h5py.ExternalLink):
        return "Link ({:s}:{:s})".format(item.filename, item.path)
    else:
        # Unknown
        return str(item.__class__)


_supports_alignment = None


def supports_alignment():
    """Check whether this version of h5py supports aligned datatypes.

    A bug in h5py 2.6 and below returns garbage for numeric aligned datatypes
    and can crash if there's a vlen member in them.

    (Aligned compound datatypes correspond to structs with padding.)
    """
    global _supports_alignment
    if _supports_alignment is not None:
        return _supports_alignment

    dt = np.dtype('i2,i8', align=True)
    ht = h5py.h5t.py_create(dt)

    _supports_alignment = (dt.itemsize == ht.get_size())
    return _supports_alignment


def extract_compound_byfield(item):
    """Extract data from a compound dataset.

    This is a workaround for a crash in h5py when "supports_alignment" is
    False.
    """
    # Even though it doesn't support alignment correctly, h5py
    # still lets us extract arrays of fields without errors
    data = np.empty(item.shape, dtype=item.dtype)
    for n in item.dtype.names:
        data[n] = item[n]
    return data

#pylint: disable=function-redefined


def _extract_array(arr):
    # Global variable allows lazily replacing this function with another
    global _extract_array
    if supports_alignment():
        def extract_array(data): return data[:]
    else:
        def extract_array(data):
            """Safely extract compound fields for older h5py versions."""
            if getattr(data.dtype, 'names', None) is not None:
                data = extract_compound_byfield(data)
            else:
                data = data[:]
            return data

    _extract_array = extract_array
    return extract_array(arr)


def extract(data):
    """Extract data from h5py data objects.

    Note that scalars will be extracted as *numpy* scalars. To obtain a native
    Python scalar such as `float`, call `result.item()`.
    """
    try:
        shape = data.shape
    except AttributeError:
        # Not a numpy/h5py object
        return data

    if shape:
        # Extract array data (possibly compound)
        data = _extract_array(data)
        if PY3 and data.size and isinstance(next(data.flat), bytes):
            # In Python 3, variable-length ASCII strings are read as bytes,
            # which causes everything else in python 3 to be super unhappy.
            # Just convert it to strings.
            data = to_native_str_array(data)
    else:
        # Extract scalar data
        try:
            data = data[()]
        except (IndexError, AttributeError):
            # IndexError occurs when trying to get data from a np.void
            # dtype, i.e. a scalar compound datatype
            pass
        except TypeError:
            # In some versions, np.string_ won't accept the scalar slice
            data = to_native_str(data)
        else:
            data = to_native_str(data)

    return data


if not h5py:
    del extract

    def extract(data): return data

