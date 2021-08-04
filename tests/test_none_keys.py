import ctypes
import unittest

from immutables.map import map_hash, map_mask, Map as PyMap
from immutables._testutils import HashKey


none_hash = map_hash(None)
assert(none_hash != 1)
assert(none_hash.bit_length() <= 32)

none_hash_u = ctypes.c_size_t(none_hash).value
not_collision = 0xffffffff & (~none_hash_u)

mask = 0x7ffffffff
none_collisions = [none_hash_u & (mask >> shift)
                   for shift in reversed(range(0, 32, 5))]
assert(len(none_collisions) == 7)
none_collisions = [
    ctypes.c_ssize_t(h | (not_collision & (mask << shift))).value
    for shift, h in zip(range(5, 37, 5), none_collisions)
]


class NoneCollision(HashKey):
    def __init__(self, name, level):
        if name is None:
            raise ValueError("Can't have a NoneCollision with a None value")
        super().__init__(none_collisions[level], name)

    def __eq__(self, other):
        if other is None:
            return False
        return super().__eq__(other)

    __hash__ = HashKey.__hash__


class BaseNoneTest:
    Map = None

    def test_none_collisions(self):
        collisions = [NoneCollision('a', level) for level in range(7)]
        indices = [map_mask(none_hash, shift) for shift in range(0, 32, 5)]

        for i, c in enumerate(collisions[:-1], 1):
            self.assertNotEqual(c, None)
            c_hash = map_hash(c)
            self.assertNotEqual(c_hash, none_hash)
            for j, idx in enumerate(indices[:i]):
                self.assertEqual(map_mask(c_hash, j*5), idx)
            for j, idx in enumerate(indices[i:], i):
                self.assertNotEqual(map_mask(c_hash, j*5), idx)

        c = collisions[-1]
        self.assertNotEqual(c, None)
        c_hash = map_hash(c)
        self.assertEqual(c_hash, none_hash)
        for i, idx in enumerate(indices):
            self.assertEqual(map_mask(c_hash, i*5), idx)

    def test_none_as_key(self):
        m = self.Map({None: 1})

        self.assertEqual(len(m), 1)
        self.assertTrue(None in m)
        self.assertEqual(m[None], 1)
        self.assertEqual(repr(m), 'immutables.Map({None: 1})')

        for level in range(7):
            key = NoneCollision('a', level)
            self.assertFalse(key in m)
            with self.assertRaises(KeyError):
                m.delete(key)

        m = m.delete(None)
        self.assertEqual(len(m), 0)
        self.assertFalse(None in m)
        self.assertEqual(repr(m), 'immutables.Map({})')

        self.assertEqual(m, self.Map())

        with self.assertRaises(KeyError):
            m.delete(None)

    def test_none_set(self):
        m = self.Map().set(None, 2)

        self.assertEqual(len(m), 1)
        self.assertTrue(None in m)
        self.assertEqual(m[None], 2)

        m = m.set(None, 1)

        self.assertEqual(len(m), 1)
        self.assertTrue(None in m)
        self.assertEqual(m[None], 1)

        m = m.delete(None)

        self.assertEqual(len(m), 0)
        self.assertEqual(m, self.Map())
        self.assertFalse(None in m)

        with self.assertRaises(KeyError):
            m.delete(None)

    def test_none_collision_1(self):
        for level in range(7):
            key = NoneCollision('a', level)
            m = self.Map({None: 1, key: 2})

            self.assertEqual(len(m), 2)
            self.assertTrue(None in m)
            self.assertEqual(m[None], 1)
            self.assertTrue(key in m)
            self.assertEqual(m[key], 2)

            m2 = m.delete(None)
            self.assertEqual(len(m2), 1)
            self.assertTrue(key in m2)
            self.assertEqual(m2[key], 2)
            self.assertFalse(None in m2)
            with self.assertRaises(KeyError):
                m2.delete(None)

            m3 = m2.delete(key)
            self.assertEqual(len(m3), 0)
            self.assertFalse(None in m3)
            self.assertFalse(key in m3)
            self.assertEqual(m3, self.Map())
            self.assertEqual(repr(m3), 'immutables.Map({})')
            with self.assertRaises(KeyError):
                m3.delete(None)
            with self.assertRaises(KeyError):
                m3.delete(key)

            m2 = m.delete(key)
            self.assertEqual(len(m2), 1)
            self.assertTrue(None in m2)
            self.assertEqual(m2[None], 1)
            self.assertFalse(key in m2)
            with self.assertRaises(KeyError):
                m2.delete(key)

            m4 = m2.delete(None)
            self.assertEqual(len(m4), 0)
            self.assertFalse(None in m4)
            self.assertFalse(key in m4)
            self.assertEqual(m4, self.Map())
            self.assertEqual(repr(m4), 'immutables.Map({})')
            with self.assertRaises(KeyError):
                m4.delete(None)
            with self.assertRaises(KeyError):
                m4.delete(key)

            self.assertEqual(m3, m4)

    def test_none_collision_2(self):
        key = HashKey(not_collision, 'a')
        m = self.Map().set(None, 1).set(key, 2)

        self.assertEqual(len(m), 2)
        self.assertTrue(key in m)
        self.assertTrue(None in m)
        self.assertEqual(m[key], 2)
        self.assertEqual

        m = m.set(None, 0)
        self.assertEqual(len(m), 2)
        self.assertTrue(key in m)
        self.assertTrue(None in m)

        for level in range(7):
            key2 = NoneCollision('b', level)
            self.assertFalse(key2 in m)
            m2 = m.set(key2, 1)

            self.assertEqual(len(m2), 3)
            self.assertTrue(key in m2)
            self.assertTrue(None in m2)
            self.assertTrue(key2 in m2)
            self.assertEqual(m2[key], 2)
            self.assertEqual(m2[None], 0)
            self.assertEqual(m2[key2], 1)

            m2 = m2.set(None, 1)
            self.assertEqual(len(m2), 3)
            self.assertTrue(key in m2)
            self.assertTrue(None in m2)
            self.assertTrue(key2 in m2)
            self.assertEqual(m2[key], 2)
            self.assertEqual(m2[None], 1)
            self.assertEqual(m2[key2], 1)

            m2 = m2.set(None, 2)
            self.assertEqual(len(m2), 3)
            self.assertTrue(key in m2)
            self.assertTrue(None in m2)
            self.assertTrue(key2 in m2)
            self.assertEqual(m2[key], 2)
            self.assertEqual(m2[None], 2)
            self.assertEqual(m2[key2], 1)

            m3 = m2.delete(key)
            self.assertEqual(len(m3), 2)
            self.assertTrue(None in m3)
            self.assertTrue(key2 in m3)
            self.assertFalse(key in m3)
            self.assertEqual(m3[None], 2)
            self.assertEqual(m3[key2], 1)
            with self.assertRaises(KeyError):
                m3.delete(key)

            m3 = m2.delete(key2)
            self.assertEqual(len(m3), 2)
            self.assertTrue(None in m3)
            self.assertTrue(key in m3)
            self.assertFalse(key2 in m3)
            self.assertEqual(m3[None], 2)
            self.assertEqual(m3[key], 2)
            with self.assertRaises(KeyError):
                m3.delete(key2)

            m3 = m2.delete(None)
            self.assertEqual(len(m3), 2)
            self.assertTrue(key in m3)
            self.assertTrue(key2 in m3)
            self.assertFalse(None in m3)
            self.assertEqual(m3[key], 2)
            self.assertEqual(m3[key2], 1)
            with self.assertRaises(KeyError):
                m3.delete(None)

        m2 = m.delete(None)
        self.assertEqual(len(m2), 1)
        self.assertFalse(None in m2)
        self.assertTrue(key in m2)
        self.assertEqual(m2[key], 2)
        with self.assertRaises(KeyError):
            m2.delete(None)

        m2 = m.delete(key)
        self.assertEqual(len(m2), 1)
        self.assertFalse(key in m2)
        self.assertTrue(None in m2)
        self.assertEqual(m2[None], 0)
        with self.assertRaises(KeyError):
            m2.delete(key)

    def test_none_collision_3(self):
        for level in range(7):
            key = NoneCollision('a', level)
            m = self.Map({key: 2})

            self.assertEqual(len(m), 1)
            self.assertFalse(None in m)
            self.assertTrue(key in m)
            self.assertEqual(m[key], 2)
            with self.assertRaises(KeyError):
                m.delete(None)

            m = m.set(None, 1)
            self.assertEqual(len(m), 2)
            self.assertTrue(key in m)
            self.assertEqual(m[key], 2)
            self.assertTrue(None in m)
            self.assertEqual(m[None], 1)

            m = m.set(None, 0)
            self.assertEqual(len(m), 2)
            self.assertTrue(key in m)
            self.assertEqual(m[key], 2)
            self.assertTrue(None in m)
            self.assertEqual(m[None], 0)

            m2 = m.delete(key)
            self.assertEqual(len(m2), 1)
            self.assertTrue(None in m2)
            self.assertEqual(m2[None], 0)
            self.assertFalse(key in m2)
            with self.assertRaises(KeyError):
                m2.delete(key)

            m2 = m.delete(None)
            self.assertEqual(len(m2), 1)
            self.assertTrue(key in m2)
            self.assertEqual(m2[key], 2)
            self.assertFalse(None in m2)
            with self.assertRaises(KeyError):
                m2.delete(None)

    def test_collision_4(self):
        key2 = NoneCollision('a', 2)
        key4 = NoneCollision('b', 4)
        m = self.Map({key2: 2, key4: 4})

        self.assertEqual(len(m), 2)
        self.assertTrue(key2 in m)
        self.assertTrue(key4 in m)
        self.assertEqual(m[key2], 2)
        self.assertEqual(m[key4], 4)
        self.assertFalse(None in m)

        m2 = m.set(None, 9)

        self.assertEqual(len(m2), 3)
        self.assertTrue(key2 in m2)
        self.assertTrue(key4 in m2)
        self.assertTrue(None in m2)
        self.assertEqual(m2[key2], 2)
        self.assertEqual(m2[key4], 4)
        self.assertEqual(m2[None], 9)

        m3 = m2.set(None, 0)
        self.assertEqual(len(m3), 3)
        self.assertTrue(key2 in m3)
        self.assertTrue(key4 in m3)
        self.assertTrue(None in m3)
        self.assertEqual(m3[key2], 2)
        self.assertEqual(m3[key4], 4)
        self.assertEqual(m3[None], 0)

        m3 = m2.set(key2, 0)
        self.assertEqual(len(m3), 3)
        self.assertTrue(key2 in m3)
        self.assertTrue(key4 in m3)
        self.assertTrue(None in m3)
        self.assertEqual(m3[key2], 0)
        self.assertEqual(m3[key4], 4)
        self.assertEqual(m3[None], 9)

        m3 = m2.set(key4, 0)
        self.assertEqual(len(m3), 3)
        self.assertTrue(key2 in m3)
        self.assertTrue(key4 in m3)
        self.assertTrue(None in m3)
        self.assertEqual(m3[key2], 2)
        self.assertEqual(m3[key4], 0)
        self.assertEqual(m3[None], 9)

        m3 = m2.delete(None)
        self.assertEqual(m3, m)
        self.assertEqual(len(m3), 2)
        self.assertTrue(key2 in m3)
        self.assertTrue(key4 in m3)
        self.assertEqual(m3[key2], 2)
        self.assertEqual(m3[key4], 4)
        self.assertFalse(None in m3)
        with self.assertRaises(KeyError):
            m3.delete(None)

        m3 = m2.delete(key2)
        self.assertEqual(len(m3), 2)
        self.assertTrue(None in m3)
        self.assertTrue(key4 in m3)
        self.assertEqual(m3[None], 9)
        self.assertEqual(m3[key4], 4)
        self.assertFalse(key2 in m3)
        with self.assertRaises(KeyError):
            m3.delete(key2)

        m3 = m2.delete(key4)
        self.assertEqual(len(m3), 2)
        self.assertTrue(None in m3)
        self.assertTrue(key2 in m3)
        self.assertEqual(m3[None], 9)
        self.assertEqual(m3[key2], 2)
        self.assertFalse(key4 in m3)
        with self.assertRaises(KeyError):
            m3.delete(key4)

    def test_none_mutation(self):
        key2 = NoneCollision('a', 2)
        key4 = NoneCollision('b', 4)
        key = NoneCollision('c', -1)
        m = self.Map({key: -1, key2: 2, key4: 4, None: 9})

        with m.mutate() as mm:
            self.assertEqual(len(mm), 4)
            self.assertTrue(key in mm)
            self.assertTrue(key2 in mm)
            self.assertTrue(key4 in mm)
            self.assertTrue(None in mm)
            self.assertEqual(mm[key2], 2)
            self.assertEqual(mm[key4], 4)
            self.assertEqual(mm[key], -1)
            self.assertEqual(mm[None], 9)

            for k in m:
                mm[k] = -mm[k]

            self.assertEqual(len(mm), 4)
            self.assertTrue(key in mm)
            self.assertTrue(key2 in mm)
            self.assertTrue(key4 in mm)
            self.assertTrue(None in mm)
            self.assertEqual(mm[key2], -2)
            self.assertEqual(mm[key4], -4)
            self.assertEqual(mm[key], 1)
            self.assertEqual(mm[None], -9)

            for k in m:
                del mm[k]
                self.assertEqual(len(mm), 3)
                self.assertFalse(k in mm)
                for n in m:
                    if n != k:
                        self.assertTrue(n in mm)
                        self.assertEqual(mm[n], -m[n])
                with self.assertRaises(KeyError):
                    del mm[k]
                mm[k] = -m[k]
                self.assertEqual(len(mm), 4)
                self.assertTrue(k in mm)
                self.assertEqual(mm[k], -m[k])

            for k in m:
                mm[k] = -mm[k]

            self.assertEqual(len(mm), 4)
            self.assertTrue(key in mm)
            self.assertTrue(key2 in mm)
            self.assertTrue(key4 in mm)
            self.assertTrue(None in mm)
            self.assertEqual(mm[key2], 2)
            self.assertEqual(mm[key4], 4)
            self.assertEqual(mm[key], -1)
            self.assertEqual(mm[None], 9)

            for k in m:
                mm[k] = -mm[k]

            self.assertEqual(len(mm), 4)
            self.assertTrue(key in mm)
            self.assertTrue(key2 in mm)
            self.assertTrue(key4 in mm)
            self.assertTrue(None in mm)
            self.assertEqual(mm[key2], -2)
            self.assertEqual(mm[key4], -4)
            self.assertEqual(mm[key], 1)
            self.assertEqual(mm[None], -9)

            m2 = mm.finish()

        self.assertEqual(set(m), set(m2))
        self.assertEqual(len(m2), 4)
        self.assertTrue(key in m2)
        self.assertTrue(key2 in m2)
        self.assertTrue(key4 in m2)
        self.assertTrue(None in m2)
        self.assertEqual(m2[key2], -2)
        self.assertEqual(m2[key4], -4)
        self.assertEqual(m2[key], 1)
        self.assertEqual(m2[None], -9)

        for k, v in m.items():
            self.assertTrue(k in m2)
            self.assertEqual(m2[k], -v)

    def test_iterators(self):
        key2 = NoneCollision('a', 2)
        key4 = NoneCollision('b', 4)
        key = NoneCollision('c', -1)
        m = self.Map({key: -1, key2: 2, key4: 4, None: 9})

        self.assertEqual(len(m), 4)
        self.assertTrue(key in m)
        self.assertTrue(key2 in m)
        self.assertTrue(key4 in m)
        self.assertTrue(None in m)
        self.assertEqual(m[key2], 2)
        self.assertEqual(m[key4], 4)
        self.assertEqual(m[key], -1)
        self.assertEqual(m[None], 9)

        s = set(m)
        self.assertEqual(len(s), 4)
        self.assertEqual(s, set([None, key, key2, key4]))

        sk = set(m.keys())
        self.assertEqual(s, sk)

        sv = set(m.values())
        self.assertEqual(len(sv), 4)
        self.assertEqual(sv, set([-1, 2, 4, 9]))

        si = set(m.items())
        self.assertEqual(len(si), 4)
        self.assertEqual(si,
                         set([(key, -1), (key2, 2), (key4, 4), (None, 9)]))

        d = {key: -1, key2: 2, key4: 4, None: 9}
        self.assertEqual(dict(m.items()), d)


class PyMapNoneTest(BaseNoneTest, unittest.TestCase):

    Map = PyMap


try:
    from immutables._map import Map as CMap
except ImportError:
    CMap = None


@unittest.skipIf(CMap is None, 'C Map is not available')
class CMapNoneTest(BaseNoneTest, unittest.TestCase):

    Map = CMap


if __name__ == "__main__":
    unittest.main()
