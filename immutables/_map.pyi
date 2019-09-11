from typing import Any
from typing import Generic
from typing import Hashable
from typing import Iterable
from typing import Iterator
from typing import Literal
from typing import Mapping
from typing import MutableMapping
from typing import NoReturn
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union


K = TypeVar('K', bound=Hashable)
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
    def __init__(
        self, col: Union[Mapping[K, V], Iterable[Tuple[K, V]]] = ..., **kw: V
    ): ...
    def __reduce__(self) -> NoReturn: ...
    def __len__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
    def update(
        self, col: Union[Mapping[K, V], Iterable[Tuple[K, V]]] = ..., **kw: V
    ) -> Map[K, V]: ...
    def mutate(self) -> MapMutation[K, V]: ...
    def set(self, key: K, val: V) -> Map[K, V]: ...
    def delete(self, key: K) -> Map[K, V]: ...
    def get(self, key: K, default: D = ...) -> Union[V, D]: ...
    def __getitem__(self, key: K) -> V: ...
    def __contains__(self, key: object) -> bool: ...
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
    def __exit__(self, *exc: Any) -> Literal[False]: ...
    def __iter__(self) -> NoReturn: ...
    def __delitem__(self, key: K) -> None: ...
    def __setitem__(self, key: K, val: V) -> None: ...
    def pop(self, __key: K, __default: D = ...) -> Union[V, D]: ...
    def get(self, key: K, default: D = ...) -> Union[V, D]: ...
    def __getitem__(self, key: K) -> V: ...
    def __contains__(self, key: Any) -> bool: ...
    def update(
        self, col: Union[Mapping[K, V], Iterable[Tuple[K, V]]] = ..., **kw: V
    ): ...
    def finish(self) -> Map[K, V]: ...
    def __len__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
