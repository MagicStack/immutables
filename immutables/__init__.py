try:
    from ._map import Map
except ImportError:
    from .map import Map


__all__ = 'Map',
__version__ = '0.3'
