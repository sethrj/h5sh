# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function,
        unicode_literals)
from six import PY3
#-----------------------------------------------------------------------------#
import h5py
import numpy as np
import os
import shlex

###############################################################################
# STRING UTILITIES
###############################################################################

def shlex_split(s, comments=False, posix=True):
    """
    Splits a string using shell lexer, but returns any incomplete string as the
    last component instead of erroring for unmatched quotations.
    """
    lex = shlex.shlex(s, posix=posix)
    lex.whitespace_split = True
    if not comments:
        lex.commenters = ''

    result = []
    while True:
        try:
            tok = lex.get_token()
        except ValueError as e:
            print(repr(e))
            # Append the current token
            result.append(lex.token)
            break
        else:
            if tok == lex.eof:
                break
        result.append(tok)
    return result

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
    except KeyError as e:
        raise ValueError("{}: No such group".format(path))
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
_INF_SYMBOL = u"\u221E" if PY3 else "inf"


def format_shape(shape):
    """Return a nicely formatted description of a dataset shape.
    """
    if not shape:
        return "scalar"
    return _MULT_SYMBOL.join(str(i) if i is not None else _INF_SYMBOL
                             for i in shape)

def items(group):
    """Generator for key/value pairs in a group, returning links where
    possible.

    The only returned link types are External or Soft. Hard links are opened
    and the corresponding item is returned.
    """
    for key in group:
        value = group.get(key, getlink=True)
        if isinstance(value, h5py.HardLink):
            # Get the actual corresponding dataset or group
            value = group[key]
        yield (key, value)

def short_describe(obj):
    """Return a short description of the given group/dataset.
    """
    if isinstance(obj, h5py.Group):
        return "Group ({:d} item{:s})".format(len(obj),
                "s" if len(obj) != 1 else "")
    elif isinstance(obj, h5py.Dataset):
        return "Dataset ({:s}: {:s})".format(
            obj.dtype.char, format_shape(obj.shape))
    elif isinstance(obj, h5py.SoftLink):
        return "Link ({:s})".format(obj.path)
    elif isinstance(obj, h5py.ExternalLink):
        filename = obj.filename
        if os.path.isabs(filename):
            filename = os.path.sep.join(['...', os.path.basename(filename)])
        return "Link ({:s}:{:s})".format(filename, obj.path)
    elif isinstance(obj, h5py.HardLink):
        return "Object"
    else:
        # Unknown
        return str(obj.__class__)

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
        data = data[:]
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

