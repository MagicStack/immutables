import sys
from typing import Any
from typing import Hashable
from typing import Iterable
from typing import Iterator
from typing import NoReturn
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union
from typing import overload

if sys.version_info >= (3, 8):
    from typing import Protocol
    from typing import TYPE_CHECKING
else:
    from typing_extensions import Protocol
    from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from ._map import Map

HT = TypeVar('HT', bound=Hashable)
KT = TypeVar('KT', bound=Hashable)
KT_co = TypeVar('KT_co', covariant=True)
MM = TypeVar('MM', bound='MapMutation[Any, Any]')
T = TypeVar('T')
VT = TypeVar('VT')
VT_co = TypeVar('VT_co', covariant=True)


class MapKeys(Protocol[KT_co]):
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[KT_co]: ...


class MapValues(Protocol[VT_co]):
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[VT_co]: ...


class MapItems(Protocol[KT_co, VT_co]):
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Tuple[KT_co, VT_co]]: ...


class IterableItems(Protocol[KT_co, VT_co]):
    def items(self) -> Iterable[Tuple[KT_co, VT_co]]: ...


class MapMutation(Protocol[KT, VT]):
    def set(self, key: KT, val: VT) -> None: ...
    def __enter__(self: MM) -> MM: ...
    def __exit__(self, *exc: Any) -> bool: ...
    def __iter__(self) -> NoReturn: ...
    def __delitem__(self, key: KT) -> None: ...
    def __setitem__(self, key: KT, val: VT) -> None: ...
    @overload
    def pop(self, __key: KT) -> VT: ...
    @overload
    def pop(self, __key: KT, __default: T) -> Union[VT, T]: ...
    @overload
    def get(self, key: KT) -> Optional[VT]: ...
    @overload
    def get(self, key: KT, default: Union[VT, T]) -> Union[VT, T]: ...
    def __getitem__(self, key: KT) -> VT: ...
    def __contains__(self, key: object) -> bool: ...

    @overload
    def update(
        self,
        __col: Union[IterableItems[KT, VT], Iterable[Tuple[KT, VT]]]
    ) -> None: ...

    @overload
    def update(
        self: 'MapMutation[Union[HT, str], Any]',
        __col: Union[IterableItems[KT, VT], Iterable[Tuple[KT, VT]]],
        **kw: VT
    ) -> None: ...
    @overload
    def update(self: 'MapMutation[Union[HT, str], Any]', **kw: VT) -> None: ...
    def finish(self) -> 'Map[KT, VT]': ...
    def __len__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
