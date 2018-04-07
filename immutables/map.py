import collections.abc
import reprlib
import sys


__all__ = ('Map',)


# Python version of _map.c.  The topmost comment there explains
# all datastructures and algorithms.
# The code here follows C code closely on purpose to make
# debugging and testing easier.


def map_hash(o):
    x = hash(o)
    return (x & 0xffffffff) ^ ((x >> 32) & 0xffffffff)


def map_mask(hash, shift):
    return (hash >> shift) & 0x01f


def map_bitpos(hash, shift):
    return 1 << map_mask(hash, shift)


def map_bitcount(v):
    v = v - ((v >> 1) & 0x55555555)
    v = (v & 0x33333333) + ((v >> 2) & 0x33333333)
    v = (v & 0x0F0F0F0F) + ((v >> 4) & 0x0F0F0F0F)
    v = v + (v >> 8)
    v = (v + (v >> 16)) & 0x3F
    return v


def map_bitindex(bitmap, bit):
    return map_bitcount(bitmap & (bit - 1))


W_EMPTY, W_NEWNODE, W_NOT_FOUND = range(3)


class BitmapNode:

    def __init__(self, size, bitmap, array):
        self.size = size
        self.bitmap = bitmap
        assert isinstance(array, list) and len(array) == size
        self.array = array

    def clone(self):
        return BitmapNode(self.size, self.bitmap, self.array.copy())

    def assoc(self, shift, hash, key, val):
        bit = map_bitpos(hash, shift)
        idx = map_bitindex(self.bitmap, bit)

        if self.bitmap & bit:
            key_idx = 2 * idx
            val_idx = key_idx + 1

            key_or_null = self.array[key_idx]
            val_or_node = self.array[val_idx]

            if key_or_null is None:
                sub_node, added = val_or_node.assoc(
                    shift + 5, hash, key, val)
                if val_or_node is sub_node:
                    return self, False

                ret = self.clone()
                ret.array[val_idx] = sub_node
                return ret, added

            if key == key_or_null:
                if val is val_or_node:
                    return self, False

                ret = self.clone()
                ret.array[val_idx] = val
                return ret, False

            existing_key_hash = map_hash(key_or_null)
            if existing_key_hash == hash:
                sub_node = CollisionNode(
                    4, hash, [key_or_null, val_or_node, key, val])
            else:
                sub_node = BitmapNode(0, 0, [])
                sub_node, _ = sub_node.assoc(
                    shift + 5, existing_key_hash,
                    key_or_null, val_or_node)
                sub_node, _ = sub_node.assoc(
                    shift + 5, hash, key, val)

            ret = self.clone()
            ret.array[key_idx] = None
            ret.array[val_idx] = sub_node
            return ret, True

        else:
            key_idx = 2 * idx
            val_idx = key_idx + 1

            n = map_bitcount(self.bitmap)

            new_array = self.array[:key_idx]
            new_array.append(key)
            new_array.append(val)
            new_array.extend(self.array[key_idx:])
            return BitmapNode(2 * (n + 1), self.bitmap | bit, new_array), True

    def find(self, shift, hash, key):
        bit = map_bitpos(hash, shift)

        if not (self.bitmap & bit):
            raise KeyError

        idx = map_bitindex(self.bitmap, bit)
        key_idx = idx * 2
        val_idx = key_idx + 1

        key_or_null = self.array[key_idx]
        val_or_node = self.array[val_idx]

        if key_or_null is None:
            return val_or_node.find(shift + 5, hash, key)

        if key == key_or_null:
            return val_or_node

        raise KeyError(key)

    def without(self, shift, hash, key):
        bit = map_bitpos(hash, shift)
        if not (self.bitmap & bit):
            return W_NOT_FOUND, None

        idx = map_bitindex(self.bitmap, bit)
        key_idx = 2 * idx
        val_idx = key_idx + 1

        key_or_null = self.array[key_idx]
        val_or_node = self.array[val_idx]

        if key_or_null is None:
            res, sub_node = val_or_node.without(shift + 5, hash, key)

            if res is W_EMPTY:
                raise RuntimeError('unreachable code')  # pragma: no cover

            elif res is W_NEWNODE:
                if (type(sub_node) is BitmapNode and
                        sub_node.size == 2 and
                        sub_node.array[0] is not None):
                    clone = self.clone()
                    clone.array[key_idx] = sub_node.array[0]
                    clone.array[val_idx] = sub_node.array[1]
                    return W_NEWNODE, clone

                clone = self.clone()
                clone.array[val_idx] = sub_node
                return W_NEWNODE, clone

            else:
                assert sub_node is None
                return res, None

        else:
            if key == key_or_null:
                if self.size == 2:
                    return W_EMPTY, None

                new_array = self.array[:key_idx]
                new_array.extend(self.array[val_idx + 1:])
                new_node = BitmapNode(
                    self.size - 2, self.bitmap & ~bit, new_array)
                return W_NEWNODE, new_node

            else:
                return W_NOT_FOUND, None

    def keys(self):
        for i in range(0, self.size, 2):
            key_or_null = self.array[i]

            if key_or_null is None:
                val_or_node = self.array[i + 1]
                yield from val_or_node.keys()
            else:
                yield key_or_null

    def values(self):
        for i in range(0, self.size, 2):
            key_or_null = self.array[i]
            val_or_node = self.array[i + 1]

            if key_or_null is None:
                yield from val_or_node.values()
            else:
                yield val_or_node

    def items(self):
        for i in range(0, self.size, 2):
            key_or_null = self.array[i]
            val_or_node = self.array[i + 1]

            if key_or_null is None:
                yield from val_or_node.items()
            else:
                yield key_or_null, val_or_node

    def dump(self, buf, level):  # pragma: no cover
        buf.append(
            '    ' * (level + 1) +
            'BitmapNode(size={} count={} bitmap={} id={:0x}):'.format(
                self.size, self.size / 2, bin(self.bitmap), id(self)))

        for i in range(0, self.size, 2):
            key_or_null = self.array[i]
            val_or_node = self.array[i + 1]

            pad = '    ' * (level + 2)

            if key_or_null is None:
                buf.append(pad + 'None:')
                val_or_node.dump(buf, level + 2)
            else:
                buf.append(pad + '{!r}: {!r}'.format(key_or_null, val_or_node))


class CollisionNode:

    def __init__(self, size, hash, array):
        self.size = size
        self.hash = hash
        self.array = array

    def find_index(self, key):
        for i in range(0, self.size, 2):
            if self.array[i] == key:
                return i
        return -1

    def find(self, shift, hash, key):
        for i in range(0, self.size, 2):
            if self.array[i] == key:
                return self.array[i + 1]
        raise KeyError(key)

    def assoc(self, shift, hash, key, val):
        if hash == self.hash:
            key_idx = self.find_index(key)

            if key_idx == -1:
                new_array = self.array.copy()
                new_array.append(key)
                new_array.append(val)
                new_node = CollisionNode(self.size + 2, hash, new_array)
                return new_node, True

            val_idx = key_idx + 1
            if self.array[val_idx] is val:
                return self, False

            new_array = self.array.copy()
            new_array[val_idx] = val
            return CollisionNode(self.size, hash, new_array), False

        else:
            new_node = BitmapNode(
                2, map_bitpos(self.hash, shift), [None, self])
            return new_node.assoc(shift, hash, key, val)

    def without(self, shift, hash, key):
        if hash != self.hash:
            return W_NOT_FOUND, None

        key_idx = self.find_index(key)
        if key_idx == -1:
            return W_NOT_FOUND, None

        new_size = self.size - 2
        if new_size == 0:
            # Shouldn't be ever reachable
            return W_EMPTY, None  # pragma: no cover

        if new_size == 2:
            if key_idx == 0:
                new_array = [self.array[2], self.array[3]]
            else:
                assert key_idx == 2
                new_array = [self.array[0], self.array[1]]

            new_node = BitmapNode(2, map_bitpos(hash, shift), new_array)
            return W_NEWNODE, new_node

        new_array = self.array[:key_idx]
        new_array.extend(self.array[key_idx + 2:])
        new_node = CollisionNode(self.size - 2, self.hash, new_array)
        return W_NEWNODE, new_node

    def keys(self):
        for i in range(0, self.size, 2):
            yield self.array[i]

    def values(self):
        for i in range(1, self.size, 2):
            yield self.array[i]

    def items(self):
        for i in range(0, self.size, 2):
            yield self.array[i], self.array[i + 1]

    def dump(self, buf, level):  # pragma: no cover
        pad = '    ' * (level + 1)
        buf.append(
            pad + 'CollisionNode(size={} id={:0x}):'.format(
                self.size, id(self)))

        pad = '    ' * (level + 2)
        for i in range(0, self.size, 2):
            key = self.array[i]
            val = self.array[i + 1]

            buf.append('{}{!r}: {!r}'.format(pad, key, val))


class GenWrapper:

    def __init__(self, count, gen):
        self.__count = count
        self.__gen = gen

    def __len__(self):
        return self.__count

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.__gen)


class Map:

    def __init__(self):
        self.__count = 0
        self.__root = BitmapNode(0, 0, [])
        self.__hash = -1

    def __len__(self):
        return self.__count

    def __eq__(self, other):
        if not isinstance(other, Map):
            return NotImplemented

        if len(self) != len(other):
            return False

        for key, val in self.__root.items():
            try:
                oval = other.__root.find(0, map_hash(key), key)
            except KeyError:
                return False
            else:
                if oval != val:
                    return False

        return True

    def set(self, key, val):
        new_count = self.__count
        new_root, added = self.__root.assoc(0, map_hash(key), key, val)

        if new_root is self.__root:
            assert not added
            return self

        if added:
            new_count += 1

        m = Map.__new__(Map)
        m.__count = new_count
        m.__root = new_root
        m.__hash = -1
        return m

    def delete(self, key):
        res, node = self.__root.without(0, map_hash(key), key)
        if res is W_EMPTY:
            return Map()
        elif res is W_NOT_FOUND:
            raise KeyError(key)
        else:
            m = Map.__new__(Map)
            m.__count = self.__count - 1
            m.__root = node
            m.__hash = -1
            return m

    def get(self, key, default=None):
        try:
            return self.__root.find(0, map_hash(key), key)
        except KeyError:
            return default

    def __getitem__(self, key):
        return self.__root.find(0, map_hash(key), key)

    def __contains__(self, key):
        try:
            self.__root.find(0, map_hash(key), key)
        except KeyError:
            return False
        else:
            return True

    def __iter__(self):
        yield from self.__root.keys()

    def keys(self):
        return GenWrapper(self.__count, self.__root.keys())

    def values(self):
        return GenWrapper(self.__count, self.__root.values())

    def items(self):
        return GenWrapper(self.__count, self.__root.items())

    def __hash__(self):
        if self.__hash != -1:
            return self.__hash

        MAX = sys.maxsize
        MASK = 2 * MAX + 1

        h = 1927868237 * (self.__count * 2 + 1)
        h &= MASK

        for key, value in self.__root.items():
            hx = hash(key)
            h ^= (hx ^ (hx << 16) ^ 89869747) * 3644798167
            h &= MASK

            hx = hash(value)
            h ^= (hx ^ (hx << 16) ^ 89869747) * 3644798167
            h &= MASK

        h = h * 69069 + 907133923
        h &= MASK

        if h > MAX:
            h -= MASK + 1  # pragma: no cover
        if h == -1:
            h = 590923713  # pragma: no cover

        self.__hash = h
        return h

    @reprlib.recursive_repr("{...}")
    def __repr__(self):
        items = []
        for key, val in self.items():
            items.append("{!r}: {!r}".format(key, val))
        return '<immutables.Map({{{}}}) at 0x{:0x}>'.format(
            ', '.join(items), id(self))

    def __dump__(self):  # pragma: no cover
        buf = []
        self.__root.dump(buf, 0)
        return '\n'.join(buf)


collections.abc.Mapping.register(Map)
