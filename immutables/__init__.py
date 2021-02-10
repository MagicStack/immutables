# flake8: noqa

from typing import TYPE_CHECKING

try:
    from ._map import Map
except ImportError:
    if TYPE_CHECKING:
        from ._map import Map
    else:
        from .map import Map
else:
    import collections.abc as _abc
    _abc.Mapping.register(Map)

from ._version import __version__

__all__ = 'Map',
