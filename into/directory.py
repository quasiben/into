from __future__ import absolute_import, division, print_function

from glob import glob
from .chunks import Chunks
from .resource import resource
from toolz import memoize, first
from datashape import discover, var
import os


class _Directory(Chunks):
    """ A directory of files on disk

    For typed containers see the ``Directory`` function which generates
    parametrized Directory classes.

    >>> from into import CSV
    >>> c = Directory(CSV)('path/to/data/')

    Normal use through resource strings

    >>> r = resource('path/to/data/*.csv')
    >>> r = resource('path/to/data/')


    """
    def __init__(self, path, **kwargs):
        self.path = path
        self.kwargs = kwargs

    def __iter__(self):
        return (resource(os.path.join(self.path, fn), **self.kwargs)
                    for fn in sorted(os.listdir(self.path)))


def Directory(cls):
    """ Parametrized DirectoryClass """
    return type('Directory(%s)' % cls.__name__, (_Directory,), {'container': cls})

Directory.__doc__ = Directory.__doc__

Directory = memoize(Directory)


@discover.register(_Directory)
def discover_Directory(c, **kwargs):
    return var * discover(first(c)).subshape[0]


@resource.register('.+' + os.path.sep + '\*\..+', priority=15)
def resource_directory(uri, **kwargs):
    path = uri.rsplit(os.path.sep, 1)[0]
    try:
        one_uri = first(glob(uri))
    except (OSError, StopIteration):
        return _Directory(path, **kwargs)
    subtype = type(resource(one_uri, **kwargs))
    return Directory(subtype)(path, **kwargs)


@resource.register('.+' + os.path.sep, priority=9)
def resource_directory_with_trailing_slash(uri, **kwargs):
    try:
        one_uri = os.listdir(uri)[0]
    except (OSError, IndexError):
        return _Directory(uri, **kwargs)
    subtype = type(resource(one_uri, **kwargs))
    return Directory(subtype)(uri, **kwargs)
