from typing import Any
from typing import Dict
from typing import Generic
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union
from typing import overload

from ._protocols import IterableItems
from ._protocols import MapItems
from ._protocols import MapKeys
from ._protocols import MapMutation
from ._protocols import MapValues
from ._protocols import HT
from ._protocols import KT
from ._protocols import T
from ._protocols import VT_co


class Map(Mapping[KT, VT_co]):
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self: Map[str, VT_co], **kw: VT_co) -> None: ...
    @overload
    def __init__(
        self, __col: Union[IterableItems[KT, VT_co], Iterable[Tuple[KT, VT_co]]]
    ) -> None: ...
    @overload
    def __init__(
        self: Map[Union[KT, str], VT_co],
        __col: Union[IterableItems[KT, VT_co], Iterable[Tuple[KT, VT_co]]],
        **kw: VT_co
    ) -> None: ...
    def __reduce__(self) -> Tuple[Type[Map[KT, VT_co]], Tuple[Dict[KT, VT_co]]]: ...
    def __len__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
    @overload
    def update(
        self,
        __col: Union[IterableItems[KT, VT_co], Iterable[Tuple[KT, VT_co]]]
    ) -> Map[KT, VT_co]: ...
    @overload
    def update(
        self: Map[Union[HT, str], Any],
        __col: Union[IterableItems[KT, VT_co], Iterable[Tuple[KT, VT_co]]],
        **kw: VT_co  # type: ignore[misc]
    ) -> Map[KT, VT_co]: ...
    @overload
    def update(
        self: Map[Union[HT, str], Any],
        **kw: VT_co  # type: ignore[misc]
    ) -> Map[KT, VT_co]: ...
    def mutate(self) -> MapMutation[KT, VT_co]: ...
    def set(self, key: KT, val: VT_co) -> Map[KT, VT_co]: ...  # type: ignore[misc]
    def delete(self, key: KT) -> Map[KT, VT_co]: ...
    @overload
    def get(self, key: KT) -> Optional[VT_co]: ...
    @overload
    def get(self, key: KT, default: Union[VT_co, T]) -> Union[VT_co, T]: ...
    def __getitem__(self, key: KT) -> VT_co: ...
    def __contains__(self, key: Any) -> bool: ...
    def __iter__(self) -> Iterator[KT]: ...
    def keys(self) -> MapKeys[KT]: ...  # type: ignore[override]
    def values(self) -> MapValues[VT_co]: ...  # type: ignore[override]
    def items(self) -> MapItems[KT, VT_co]: ...  # type: ignore[override]
    def __hash__(self) -> int: ...
    def __dump__(self) -> str: ...
    def __class_getitem__(cls, item: Any) -> Type[Map[Any, Any]]: ...
