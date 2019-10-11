try:
    from ._map import Map
except ImportError:
    from .map import Map
else:
    import collections.abc as _abc
    _abc.Mapping.register(Map)


__all__ = 'Map',
__version__ = '0.11'
