# flake8: noqa

try:
    from ._map import Map
except ImportError:
    from .map import Map
else:
    import collections.abc as _abc
    _abc.Mapping.register(Map)

from ._version import __version__

__all__ = 'Map',
