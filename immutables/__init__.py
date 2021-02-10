# flake8: noqa

import sys

if sys.version_info >= (3, 5, 2):
    from typing import TYPE_CHECKING
else:
    from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from ._map import Map
else:
    try:
        from ._map import Map
    except ImportError:
        from .map import Map
    else:
        import collections.abc as _abc
        _abc.Mapping.register(Map)

from ._protocols import MapKeys as MapKeys
from ._protocols import MapValues as MapValues
from ._protocols import MapItems as MapItems
from ._protocols import MapMutation as MapMutation

from ._version import __version__

__all__ = 'Map',
