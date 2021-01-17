from typing import Any
from typing import Generic
from typing import Hashable
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import MutableMapping
from typing import NoReturn
from typing import overload
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import Optional


K = TypeVar('K', bound=Hashable)
C = TypeVar('C', bound=Hashable)
V = TypeVar('V', bound=Any)
D = TypeVar('D', bound=Any)


class BitmapNode: ...


class MapKeys(Generic[K]):
    def __init__(self, c: int, m: BitmapNode) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[K]: ...


class MapValues(Generic[V]):
    def __init__(self, c: int, m: BitmapNode) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[V]: ...


class MapItems(Generic[K, V]):
    def __init__(self, c: int, m: BitmapNode) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Tuple[K, V]]: ...


class Map(Mapping[K, V]):
    @overload
    def __init__(self: Map[Any, Any]) -> None: ...

    @overload
    def __init__(self: Map[str, V], **kw: V) -> None: ...

    @overload
    def __init__(
        self, col: Union[Mapping[K, V], Iterable[Tuple[K, V]]]
    ) -> None: ...
    @overload
    def __init__(
        self: Map[Union[C, str], V],
        col: Union[Mapping[C, V], Iterable[Tuple[C, V]]],
        **kw: V
    ) -> None: ...

    def __reduce__(self) -> Tuple[Type[Map], Tuple[dict]]: ...
    def __len__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...

    @overload
    def update(self, **kw: D) -> Map[Union[K, str], Union[V, D]]: ...
    # The overloads are overlapping, but not really.
    # A call with no kwargs doesn't add string keys, so
    # Map({1: "a"}).update({2: "b"}) produces Map[int, str], but
    # Map({1: "a"}).update(two="b") produces Map[int|str, str]
    @overload
    def update( # type: ignore
        self,
        col: Union[Mapping[C, D], Iterable[Tuple[C, D]]]
    ) -> Map[Union[K, C], Union[V, D]]: ...
    @overload
    def update(
        self,
        col: Union[Mapping[C, D], Iterable[Tuple[C, D]]],
        **kw: D
    ) -> Map[Union[K, C, str], Union[V, D]]: ...

    def mutate(self) -> MapMutation[K, V]: ...
    def set(self, key: C, val: D) -> Map[Union[K, C], Union[V, D]]: ...
    def delete(self, key: K) -> Map[K, V]: ...
    def get(self, key: K) -> Optional[V]: ...
    def get(self, key: K, default: D = ...) -> Union[V, D]: ...
    def __getitem__(self, key: K) -> V: ...
    def __contains__(self, key: Any) -> bool: ...
    def __iter__(self) -> Iterator[K]: ...
    def keys(self) -> MapKeys[K]: ...
    def values(self) -> MapValues[V]: ...
    def items(self) -> MapItems[K, V]: ...
    def __hash__(self) -> int: ...
    def __dump__(self) -> str: ...
    def __class_getitem__(cls, item: Any) -> Type[Map]: ...


S = TypeVar('S', bound='MapMutation')


class MapMutation(MutableMapping[K, V]):
    def __init__(self, count: int, root: BitmapNode) -> None: ...
    def set(self, key: K, val: V) -> None: ...
    def __enter__(self: S) -> S: ...
    def __exit__(self, *exc: Any): ...
    def __iter__(self) -> NoReturn: ...
    def __delitem__(self, key: K) -> None: ...
    def __setitem__(self, key: K, val: V) -> None: ...
    def pop(self, __key: K, __default: D = ...) -> Union[V, D]: ...
    def get(self, key: K, default: D = ...) -> Union[V, D]: ...
    def __getitem__(self, key: K) -> V: ...
    def __contains__(self, key: Any) -> bool: ...
    @overload
    def update(self: MapMutation[Union[C, str], V], **kw: V) -> None: ...
    @overload
    def update(
        self, col: Union[Mapping[K, V], Iterable[Tuple[K, V]]]
    ) -> None: ...
    @overload
    def update(
        self: MapMutation[Union[C, str], V],
        col: Union[Mapping[K, V], Iterable[Tuple[K, V]]],
        **kw: V
    ) -> None: ...
    def finish(self) -> Map[K, V]: ...
    def __len__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
