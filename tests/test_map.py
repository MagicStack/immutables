import collections.abc
import gc
import pickle
import random
import sys
import unittest
import weakref

from immutables.map import Map as PyMap
from immutables._testutils import EqError
from immutables._testutils import HashKey
from immutables._testutils import HashKeyCrasher
from immutables._testutils import HashingError
from immutables._testutils import KeyStr
from immutables._testutils import ReprError


class BaseMapTest:

    Map = None

    def test_hashkey_helper_1(self):
        k1 = HashKey(10, 'aaa')
        k2 = HashKey(10, 'bbb')

        self.assertNotEqual(k1, k2)
        self.assertEqual(hash(k1), hash(k2))

        d = dict()
        d[k1] = 'a'
        d[k2] = 'b'

        self.assertEqual(d[k1], 'a')
        self.assertEqual(d[k2], 'b')

    def test_map_basics_1(self):
        h = self.Map()
        h = None  # NoQA

    def test_map_basics_2(self):
        h = self.Map()
        self.assertEqual(len(h), 0)

        h2 = h.set('a', 'b')
        self.assertIsNot(h, h2)
        self.assertEqual(len(h), 0)
        self.assertEqual(len(h2), 1)

        self.assertIsNone(h.get('a'))
        self.assertEqual(h.get('a', 42), 42)

        self.assertEqual(h2.get('a'), 'b')

        h3 = h2.set('b', 10)
        self.assertIsNot(h2, h3)
        self.assertEqual(len(h), 0)
        self.assertEqual(len(h2), 1)
        self.assertEqual(len(h3), 2)
        self.assertEqual(h3.get('a'), 'b')
        self.assertEqual(h3.get('b'), 10)

        self.assertIsNone(h.get('b'))
        self.assertIsNone(h2.get('b'))

        self.assertIsNone(h.get('a'))
        self.assertEqual(h2.get('a'), 'b')

        h = h2 = h3 = None

    def test_map_basics_3(self):
        h = self.Map()
        o = object()
        h1 = h.set('1', o)
        h2 = h1.set('1', o)
        self.assertIs(h1, h2)

    def test_map_basics_4(self):
        h = self.Map()
        h1 = h.set('key', [])
        h2 = h1.set('key', [])
        self.assertIsNot(h1, h2)
        self.assertEqual(len(h1), 1)
        self.assertEqual(len(h2), 1)
        self.assertIsNot(h1.get('key'), h2.get('key'))

    def test_map_collision_1(self):
        k1 = HashKey(10, 'aaa')
        k2 = HashKey(10, 'bbb')
        k3 = HashKey(10, 'ccc')

        h = self.Map()
        h2 = h.set(k1, 'a')
        h3 = h2.set(k2, 'b')

        self.assertEqual(h.get(k1), None)
        self.assertEqual(h.get(k2), None)

        self.assertEqual(h2.get(k1), 'a')
        self.assertEqual(h2.get(k2), None)

        self.assertEqual(h3.get(k1), 'a')
        self.assertEqual(h3.get(k2), 'b')

        h4 = h3.set(k2, 'cc')
        h5 = h4.set(k3, 'aa')

        self.assertEqual(h3.get(k1), 'a')
        self.assertEqual(h3.get(k2), 'b')
        self.assertEqual(h4.get(k1), 'a')
        self.assertEqual(h4.get(k2), 'cc')
        self.assertEqual(h4.get(k3), None)
        self.assertEqual(h5.get(k1), 'a')
        self.assertEqual(h5.get(k2), 'cc')
        self.assertEqual(h5.get(k2), 'cc')
        self.assertEqual(h5.get(k3), 'aa')

        self.assertEqual(len(h), 0)
        self.assertEqual(len(h2), 1)
        self.assertEqual(len(h3), 2)
        self.assertEqual(len(h4), 2)
        self.assertEqual(len(h5), 3)

    def test_map_collision_2(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(0b011000011100000100, 'C')
        D = HashKey(0b011000011100000100, 'D')
        E = HashKey(0b1011000011100000100, 'E')

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')

        # BitmapNode(size=6 bitmap=0b100110000):
        #     NULL:
        #         BitmapNode(size=4 bitmap=0b1000000000000000000001000):
        #             <Key name:A hash:100>: 'a'
        #             NULL:
        #                 CollisionNode(size=4 id=0x108572410):
        #                     <Key name:C hash:100100>: 'c'
        #                     <Key name:D hash:100100>: 'd'
        #     <Key name:B hash:101>: 'b'

        h = h.set(E, 'e')

        # BitmapNode(size=4 count=2.0 bitmap=0b110000 id=10b8ea5c0):
        #     None:
        #         BitmapNode(size=4 count=2.0
        #                    bitmap=0b1000000000000000000001000 id=10b8ea518):
        #             <Key name:A hash:100>: 'a'
        #             None:
        #                 BitmapNode(size=2 count=1.0 bitmap=0b10
        #                            id=10b8ea4a8):
        #                     None:
        #                         BitmapNode(size=4 count=2.0
        #                                    bitmap=0b100000001000
        #                                    id=10b8ea4e0):
        #                             None:
        #                                 CollisionNode(size=4 id=10b8ea470):
        #                                     <Key name:C hash:100100>: 'c'
        #                                     <Key name:D hash:100100>: 'd'
        #                             <Key name:E hash:362244>: 'e'
        #     <Key name:B hash:101>: 'b'

    def test_map_stress_01(self):
        COLLECTION_SIZE = 7000
        TEST_ITERS_EVERY = 647
        CRASH_HASH_EVERY = 97
        CRASH_EQ_EVERY = 11
        RUN_XTIMES = 3

        for _ in range(RUN_XTIMES):
            h = self.Map()
            d = dict()

            for i in range(COLLECTION_SIZE):
                key = KeyStr(i)

                if not (i % CRASH_HASH_EVERY):
                    with HashKeyCrasher(error_on_hash=True):
                        with self.assertRaises(HashingError):
                            h.set(key, i)

                h = h.set(key, i)

                if not (i % CRASH_EQ_EVERY):
                    with HashKeyCrasher(error_on_eq=True):
                        with self.assertRaises(EqError):
                            h.get(KeyStr(i))  # really trigger __eq__

                d[key] = i
                self.assertEqual(len(d), len(h))

                if not (i % TEST_ITERS_EVERY):
                    self.assertEqual(set(h.items()), set(d.items()))
                    self.assertEqual(len(h.items()), len(d.items()))

            self.assertEqual(len(h), COLLECTION_SIZE)

            for key in range(COLLECTION_SIZE):
                self.assertEqual(h.get(KeyStr(key), 'not found'), key)

            keys_to_delete = list(range(COLLECTION_SIZE))
            random.shuffle(keys_to_delete)
            for iter_i, i in enumerate(keys_to_delete):
                key = KeyStr(i)

                if not (iter_i % CRASH_HASH_EVERY):
                    with HashKeyCrasher(error_on_hash=True):
                        with self.assertRaises(HashingError):
                            h.delete(key)

                if not (iter_i % CRASH_EQ_EVERY):
                    with HashKeyCrasher(error_on_eq=True):
                        with self.assertRaises(EqError):
                            h.delete(KeyStr(i))

                h = h.delete(key)
                self.assertEqual(h.get(key, 'not found'), 'not found')
                del d[key]
                self.assertEqual(len(d), len(h))

                if iter_i == COLLECTION_SIZE // 2:
                    hm = h
                    dm = d.copy()

                if not (iter_i % TEST_ITERS_EVERY):
                    self.assertEqual(set(h.keys()), set(d.keys()))
                    self.assertEqual(len(h.keys()), len(d.keys()))

            self.assertEqual(len(d), 0)
            self.assertEqual(len(h), 0)

            # ============

            for key in dm:
                self.assertEqual(hm.get(str(key)), dm[key])
            self.assertEqual(len(dm), len(hm))

            for i, key in enumerate(keys_to_delete):
                if str(key) in dm:
                    hm = hm.delete(str(key))
                    dm.pop(str(key))
                self.assertEqual(hm.get(str(key), 'not found'), 'not found')
                self.assertEqual(len(d), len(h))

                if not (i % TEST_ITERS_EVERY):
                    self.assertEqual(set(h.values()), set(d.values()))
                    self.assertEqual(len(h.values()), len(d.values()))

            self.assertEqual(len(d), 0)
            self.assertEqual(len(h), 0)
            self.assertEqual(list(h.items()), [])

    def test_map_stress_02(self):
        COLLECTION_SIZE = 20000
        TEST_ITERS_EVERY = 647
        CRASH_HASH_EVERY = 97
        DELETE_EVERY = 3
        CRASH_EQ_EVERY = 11

        h = self.Map()
        d = dict()

        for i in range(COLLECTION_SIZE // 2):
            key = KeyStr(i)

            if not (i % CRASH_HASH_EVERY):
                with HashKeyCrasher(error_on_hash=True):
                    with self.assertRaises(HashingError):
                        h.set(key, i)

            h = h.set(key, i)

            if not (i % CRASH_EQ_EVERY):
                with HashKeyCrasher(error_on_eq=True):
                    with self.assertRaises(EqError):
                        h.get(KeyStr(i))  # really trigger __eq__

            d[key] = i
            self.assertEqual(len(d), len(h))

            if not (i % TEST_ITERS_EVERY):
                self.assertEqual(set(h.items()), set(d.items()))
                self.assertEqual(len(h.items()), len(d.items()))

        with h.mutate() as m:
            for i in range(COLLECTION_SIZE // 2, COLLECTION_SIZE):
                key = KeyStr(i)

                if not (i % CRASH_HASH_EVERY):
                    with HashKeyCrasher(error_on_hash=True):
                        with self.assertRaises(HashingError):
                            m[key] = i

                m[key] = i

                if not (i % CRASH_EQ_EVERY):
                    with HashKeyCrasher(error_on_eq=True):
                        with self.assertRaises(EqError):
                            m[KeyStr(i)]

                d[key] = i
                self.assertEqual(len(d), len(m))

                if not (i % DELETE_EVERY):
                    del m[key]
                    del d[key]

                self.assertEqual(len(d), len(m))

            h = m.finish()

        self.assertEqual(len(h), len(d))
        self.assertEqual(set(h.items()), set(d.items()))

        with h.mutate() as m:
            for key in list(d):
                del d[key]
                del m[key]
                self.assertEqual(len(m), len(d))
            h = m.finish()

        self.assertEqual(len(h), len(d))
        self.assertEqual(set(h.items()), set(d.items()))

    def test_map_delete_1(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(102, 'C')
        D = HashKey(103, 'D')
        E = HashKey(104, 'E')
        Z = HashKey(-100, 'Z')

        Er = HashKey(103, 'Er', error_on_eq_to=D)

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')

        orig_len = len(h)

        # BitmapNode(size=10 bitmap=0b111110000 id=0x10eadc618):
        #     <Key name:A hash:100>: 'a'
        #     <Key name:B hash:101>: 'b'
        #     <Key name:C hash:102>: 'c'
        #     <Key name:D hash:103>: 'd'
        #     <Key name:E hash:104>: 'e'

        h = h.delete(C)
        self.assertEqual(len(h), orig_len - 1)

        with self.assertRaisesRegex(ValueError, 'cannot compare'):
            h.delete(Er)

        h = h.delete(D)
        self.assertEqual(len(h), orig_len - 2)

        with self.assertRaises(KeyError) as ex:
            h.delete(Z)
        self.assertIs(ex.exception.args[0], Z)

        h = h.delete(A)
        self.assertEqual(len(h), orig_len - 3)

        self.assertEqual(h.get(A, 42), 42)
        self.assertEqual(h.get(B), 'b')
        self.assertEqual(h.get(E), 'e')

    def test_map_delete_2(self):
        A = HashKey(100, 'A')
        B = HashKey(201001, 'B')
        C = HashKey(101001, 'C')
        BLike = HashKey(201001, 'B-like')
        D = HashKey(103, 'D')
        E = HashKey(104, 'E')
        Z = HashKey(-100, 'Z')

        Er = HashKey(201001, 'Er', error_on_eq_to=B)

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')

        h = h.set(B, 'b')  # trigger branch in BitmapNode.assoc

        with self.assertRaises(KeyError):
            h.delete(BLike)    # trigger branch in BitmapNode.without

        orig_len = len(h)

        # BitmapNode(size=8 bitmap=0b1110010000):
        #     <Key name:A hash:100>: 'a'
        #     <Key name:D hash:103>: 'd'
        #     <Key name:E hash:104>: 'e'
        #     NULL:
        #         BitmapNode(size=4 bitmap=0b100000000001000000000):
        #             <Key name:B hash:201001>: 'b'
        #             <Key name:C hash:101001>: 'c'

        with self.assertRaisesRegex(ValueError, 'cannot compare'):
            h.delete(Er)

        with self.assertRaises(KeyError) as ex:
            h.delete(Z)
        self.assertIs(ex.exception.args[0], Z)
        self.assertEqual(len(h), orig_len)

        h = h.delete(C)
        self.assertEqual(len(h), orig_len - 1)

        h = h.delete(B)
        self.assertEqual(len(h), orig_len - 2)

        h = h.delete(A)
        self.assertEqual(len(h), orig_len - 3)

        self.assertEqual(h.get(D), 'd')
        self.assertEqual(h.get(E), 'e')

        with self.assertRaises(KeyError):
            h = h.delete(A)
        with self.assertRaises(KeyError):
            h = h.delete(B)
        h = h.delete(D)
        h = h.delete(E)
        self.assertEqual(len(h), 0)

    def test_map_delete_3(self):
        A = HashKey(0b00000000001100100, 'A')
        B = HashKey(0b00000000001100101, 'B')

        C = HashKey(0b11000011100000100, 'C')
        D = HashKey(0b11000011100000100, 'D')
        X = HashKey(0b01000011100000100, 'Z')
        Y = HashKey(0b11000011100000100, 'Y')

        E = HashKey(0b00000000001101000, 'E')

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')

        self.assertEqual(len(h), 5)
        h = h.set(C, 'c')  # trigger branch in CollisionNode.assoc
        self.assertEqual(len(h), 5)

        orig_len = len(h)

        with self.assertRaises(KeyError):
            h.delete(X)
        with self.assertRaises(KeyError):
            h.delete(Y)

        # BitmapNode(size=6 bitmap=0b100110000):
        #     NULL:
        #         BitmapNode(size=4 bitmap=0b1000000000000000000001000):
        #             <Key name:A hash:100>: 'a'
        #             NULL:
        #                 CollisionNode(size=4 id=0x108572410):
        #                     <Key name:C hash:100100>: 'c'
        #                     <Key name:D hash:100100>: 'd'
        #     <Key name:B hash:101>: 'b'
        #     <Key name:E hash:104>: 'e'

        h = h.delete(A)
        self.assertEqual(len(h), orig_len - 1)

        h = h.delete(E)
        self.assertEqual(len(h), orig_len - 2)

        self.assertEqual(h.get(C), 'c')
        self.assertEqual(h.get(B), 'b')

        h2 = h.delete(C)
        self.assertEqual(len(h2), orig_len - 3)

        h2 = h.delete(D)
        self.assertEqual(len(h2), orig_len - 3)

        self.assertEqual(len(h), orig_len - 2)

    def test_map_delete_4(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(100100, 'E')

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')

        orig_len = len(h)

        # BitmapNode(size=4 bitmap=0b110000):
        #     NULL:
        #         BitmapNode(size=4 bitmap=0b1000000000000000000001000):
        #             <Key name:A hash:100>: 'a'
        #             NULL:
        #                 CollisionNode(size=6 id=0x10515ef30):
        #                     <Key name:C hash:100100>: 'c'
        #                     <Key name:D hash:100100>: 'd'
        #                     <Key name:E hash:100100>: 'e'
        #     <Key name:B hash:101>: 'b'

        h = h.delete(D)
        self.assertEqual(len(h), orig_len - 1)

        h = h.delete(E)
        self.assertEqual(len(h), orig_len - 2)

        h = h.delete(C)
        self.assertEqual(len(h), orig_len - 3)

        h = h.delete(A)
        self.assertEqual(len(h), orig_len - 4)

        h = h.delete(B)
        self.assertEqual(len(h), 0)

    def test_map_delete_5(self):
        h = self.Map()

        keys = []
        for i in range(17):
            key = HashKey(i, str(i))
            keys.append(key)
            h = h.set(key, 'val-{}'.format(i))

        collision_key16 = HashKey(16, '18')
        h = h.set(collision_key16, 'collision')

        # ArrayNode(id=0x10f8b9318):
        #     0::
        #     BitmapNode(size=2 count=1 bitmap=0b1):
        #         <Key name:0 hash:0>: 'val-0'
        #
        # ... 14 more BitmapNodes ...
        #
        #     15::
        #     BitmapNode(size=2 count=1 bitmap=0b1):
        #         <Key name:15 hash:15>: 'val-15'
        #
        #     16::
        #     BitmapNode(size=2 count=1 bitmap=0b1):
        #         NULL:
        #             CollisionNode(size=4 id=0x10f2f5af8):
        #                 <Key name:16 hash:16>: 'val-16'
        #                 <Key name:18 hash:16>: 'collision'

        self.assertEqual(len(h), 18)

        h = h.delete(keys[2])
        self.assertEqual(len(h), 17)

        h = h.delete(collision_key16)
        self.assertEqual(len(h), 16)
        h = h.delete(keys[16])
        self.assertEqual(len(h), 15)

        h = h.delete(keys[1])
        self.assertEqual(len(h), 14)
        with self.assertRaises(KeyError) as ex:
            h.delete(keys[1])
        self.assertIs(ex.exception.args[0], keys[1])
        self.assertEqual(len(h), 14)

        for key in keys:
            if key in h:
                h = h.delete(key)
        self.assertEqual(len(h), 0)

    def test_map_delete_6(self):
        h = self.Map()
        h = h.set(1, 1)
        h = h.delete(1)
        self.assertEqual(len(h), 0)
        self.assertEqual(h, self.Map())

    def test_map_items_1(self):
        A = HashKey(100, 'A')
        B = HashKey(201001, 'B')
        C = HashKey(101001, 'C')
        D = HashKey(103, 'D')
        E = HashKey(104, 'E')
        F = HashKey(110, 'F')

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')
        h = h.set(F, 'f')

        it = h.items()
        self.assertEqual(
            set(list(it)),
            {(A, 'a'), (B, 'b'), (C, 'c'), (D, 'd'), (E, 'e'), (F, 'f')})

    def test_map_items_2(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(100100, 'E')
        F = HashKey(110, 'F')

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')
        h = h.set(F, 'f')

        it = h.items()
        self.assertEqual(
            set(list(it)),
            {(A, 'a'), (B, 'b'), (C, 'c'), (D, 'd'), (E, 'e'), (F, 'f')})

    def test_map_items_3(self):
        h = self.Map()
        self.assertEqual(len(h.items()), 0)
        self.assertEqual(list(h.items()), [])

    def test_map_items_4(self):
        h = self.Map(a=1, b=2, c=3)
        k = h.items()
        self.assertEqual(set(k), {('a', 1), ('b', 2), ('c', 3)})
        self.assertEqual(set(k), {('a', 1), ('b', 2), ('c', 3)})

    def test_map_keys_1(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(100100, 'E')
        F = HashKey(110, 'F')

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')
        h = h.set(F, 'f')

        self.assertEqual(set(list(h.keys())), {A, B, C, D, E, F})
        self.assertEqual(set(list(h)), {A, B, C, D, E, F})

    def test_map_keys_2(self):
        h = self.Map(a=1, b=2, c=3)
        k = h.keys()
        self.assertEqual(set(k), {'a', 'b', 'c'})
        self.assertEqual(set(k), {'a', 'b', 'c'})

    def test_map_values_1(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(100100, 'E')
        F = HashKey(110, 'F')

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')
        h = h.set(F, 'f')

        self.assertEqual(set(list(h.values())), {'a', 'b', 'c', 'd', 'e', 'f'})

    def test_map_values_2(self):
        h = self.Map(a=1, b=2, c=3)
        k = h.values()
        self.assertEqual(set(k), {1, 2, 3})
        self.assertEqual(set(k), {1, 2, 3})

    def test_map_eq_1(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(120, 'E')

        h1 = self.Map()
        h1 = h1.set(A, 'a')
        h1 = h1.set(B, 'b')
        h1 = h1.set(C, 'c')
        h1 = h1.set(D, 'd')

        h2 = self.Map()
        h2 = h2.set(A, 'a')

        self.assertFalse(h1 == h2)
        self.assertTrue(h1 != h2)

        h2 = h2.set(B, 'b')
        self.assertFalse(h1 == h2)
        self.assertTrue(h1 != h2)

        h2 = h2.set(C, 'c')
        self.assertFalse(h1 == h2)
        self.assertTrue(h1 != h2)

        h2 = h2.set(D, 'd2')
        self.assertFalse(h1 == h2)
        self.assertTrue(h1 != h2)

        h2 = h2.set(D, 'd')
        self.assertTrue(h1 == h2)
        self.assertFalse(h1 != h2)

        h2 = h2.set(E, 'e')
        self.assertFalse(h1 == h2)
        self.assertTrue(h1 != h2)

        h2 = h2.delete(D)
        self.assertFalse(h1 == h2)
        self.assertTrue(h1 != h2)

        h2 = h2.set(E, 'd')
        self.assertFalse(h1 == h2)
        self.assertTrue(h1 != h2)

    def test_map_eq_2(self):
        A = HashKey(100, 'A')
        Er = HashKey(100, 'Er', error_on_eq_to=A)

        h1 = self.Map()
        h1 = h1.set(A, 'a')

        h2 = self.Map()
        h2 = h2.set(Er, 'a')

        with self.assertRaisesRegex(ValueError, 'cannot compare'):
            h1 == h2

        with self.assertRaisesRegex(ValueError, 'cannot compare'):
            h1 != h2

    def test_map_eq_3(self):
        self.assertNotEqual(self.Map(), 1)

    def test_map_gc_1(self):
        A = HashKey(100, 'A')

        h = self.Map()
        h = h.set(0, 0)  # empty Map node is memoized in _map.c
        ref = weakref.ref(h)

        a = []
        a.append(a)
        a.append(h)
        b = []
        a.append(b)
        b.append(a)
        h = h.set(A, b)

        del h, a, b

        gc.collect()
        gc.collect()
        gc.collect()

        self.assertIsNone(ref())

    def test_map_gc_2(self):
        A = HashKey(100, 'A')

        h = self.Map()
        h = h.set(A, 'a')
        h = h.set(A, h)

        ref = weakref.ref(h)
        hi = iter(h.items())
        next(hi)

        del h, hi

        gc.collect()
        gc.collect()
        gc.collect()

        self.assertIsNone(ref())

    def test_map_in_1(self):
        A = HashKey(100, 'A')
        AA = HashKey(100, 'A')

        B = HashKey(101, 'B')

        h = self.Map()
        h = h.set(A, 1)

        self.assertTrue(A in h)
        self.assertFalse(B in h)

        with self.assertRaises(EqError):
            with HashKeyCrasher(error_on_eq=True):
                AA in h

        with self.assertRaises(HashingError):
            with HashKeyCrasher(error_on_hash=True):
                AA in h

    def test_map_getitem_1(self):
        A = HashKey(100, 'A')
        AA = HashKey(100, 'A')

        B = HashKey(101, 'B')

        h = self.Map()
        h = h.set(A, 1)

        self.assertEqual(h[A], 1)
        self.assertEqual(h[AA], 1)

        with self.assertRaises(KeyError):
            h[B]

        with self.assertRaises(EqError):
            with HashKeyCrasher(error_on_eq=True):
                h[AA]

        with self.assertRaises(HashingError):
            with HashKeyCrasher(error_on_hash=True):
                h[AA]

    def test_repr_1(self):
        h = self.Map()
        self.assertEqual(repr(h), 'immutables.Map({})')

        h = h.set(1, 2).set(2, 3).set(3, 4)
        self.assertEqual(repr(h), 'immutables.Map({1: 2, 2: 3, 3: 4})')

    def test_repr_2(self):
        h = self.Map()
        A = HashKey(100, 'A')

        with self.assertRaises(ReprError):
            with HashKeyCrasher(error_on_repr=True):
                repr(h.set(1, 2).set(A, 3).set(3, 4))

        with self.assertRaises(ReprError):
            with HashKeyCrasher(error_on_repr=True):
                repr(h.set(1, 2).set(2, A).set(3, 4))

    def test_repr_3(self):
        class Key:
            def __init__(self):
                self.val = None

            def __hash__(self):
                return 123

            def __repr__(self):
                return repr(self.val)

        h = self.Map()
        k = Key()
        h = h.set(k, 1)
        k.val = h

        self.assertEqual(repr(h), 'immutables.Map({{...}: 1})')

    def test_hash_1(self):
        h = self.Map()
        self.assertNotEqual(hash(h), -1)
        self.assertEqual(hash(h), hash(h))

        h = h.set(1, 2).set('a', 'b')
        self.assertNotEqual(hash(h), -1)
        self.assertEqual(hash(h), hash(h))

        self.assertEqual(
            hash(h.set(1, 2).set('a', 'b')),
            hash(h.set('a', 'b').set(1, 2)))

    def test_hash_2(self):
        h = self.Map()
        A = HashKey(100, 'A')

        m = h.set(1, 2).set(A, 3).set(3, 4)
        with self.assertRaises(HashingError):
            with HashKeyCrasher(error_on_hash=True):
                hash(m)

        m = h.set(1, 2).set(2, A).set(3, 4)
        with self.assertRaises(HashingError):
            with HashKeyCrasher(error_on_hash=True):
                hash(m)

    def test_abc_1(self):
        self.assertTrue(issubclass(self.Map, collections.abc.Mapping))

    def test_map_mut_1(self):
        h = self.Map()
        h = h.set('a', 1)

        hm1 = h.mutate()
        hm2 = h.mutate()

        self.assertFalse(isinstance(hm1, self.Map))

        self.assertIsNot(hm1, hm2)
        self.assertEqual(hm1['a'], 1)
        self.assertEqual(hm2['a'], 1)

        hm1.set('b', 2)
        hm1.set('c', 3)

        hm2.set('x', 100)
        hm2.set('a', 1000)

        self.assertEqual(hm1['a'], 1)
        self.assertEqual(hm1.get('x', -1), -1)

        self.assertEqual(hm2['a'], 1000)
        self.assertTrue('x' in hm2)

        h1 = hm1.finish()
        h2 = hm2.finish()

        self.assertTrue(isinstance(h1, self.Map))

        self.assertEqual(dict(h.items()), {'a': 1})
        self.assertEqual(dict(h1.items()), {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(dict(h2.items()), {'a': 1000, 'x': 100})

    def test_map_mut_2(self):
        h = self.Map()
        h = h.set('a', 1)

        hm1 = h.mutate()
        hm1.set('a', 2)
        hm1.set('a', 3)
        hm1.set('a', 4)
        h2 = hm1.finish()

        self.assertEqual(dict(h.items()), {'a': 1})
        self.assertEqual(dict(h2.items()), {'a': 4})

    def test_map_mut_3(self):
        h = self.Map()
        h = h.set('a', 1)
        hm1 = h.mutate()

        self.assertEqual(repr(hm1), "immutables.MapMutation({'a': 1})")

        with self.assertRaisesRegex(TypeError, 'unhashable type'):
            hash(hm1)

    def test_map_mut_4(self):
        h = self.Map()
        h = h.set('a', 1)
        h = h.set('b', 2)

        hm1 = h.mutate()
        hm2 = h.mutate()

        self.assertEqual(hm1, hm2)

        hm1.set('a', 10)
        self.assertNotEqual(hm1, hm2)

        hm2.set('a', 10)
        self.assertEqual(hm1, hm2)

        self.assertEqual(hm2.pop('a'), 10)
        self.assertNotEqual(hm1, hm2)

    def test_map_mut_5(self):
        h = self.Map({'a': 1, 'b': 2}, z=100)
        self.assertTrue(isinstance(h, self.Map))
        self.assertEqual(dict(h.items()), {'a': 1, 'b': 2, 'z': 100})

        h2 = h.update(z=200, y=-1)
        self.assertEqual(dict(h.items()), {'a': 1, 'b': 2, 'z': 100})
        self.assertEqual(dict(h2.items()), {'a': 1, 'b': 2, 'z': 200, 'y': -1})

        h3 = h2.update([(1, 2), (3, 4)])
        self.assertEqual(dict(h.items()), {'a': 1, 'b': 2, 'z': 100})
        self.assertEqual(dict(h2.items()), {'a': 1, 'b': 2, 'z': 200, 'y': -1})
        self.assertEqual(dict(h3.items()),
                         {'a': 1, 'b': 2, 'z': 200, 'y': -1, 1: 2, 3: 4})

        h4 = h3.update()
        self.assertIs(h4, h3)

        h5 = h4.update(self.Map({'zzz': 'yyz'}))

        self.assertEqual(dict(h5.items()),
                         {'a': 1, 'b': 2, 'z': 200, 'y': -1, 1: 2, 3: 4,
                          'zzz': 'yyz'})

    def test_map_mut_6(self):
        h = self.Map({'a': 1, 'b': 2}, z=100)
        self.assertEqual(dict(h.items()), {'a': 1, 'b': 2, 'z': 100})

        with self.assertRaisesRegex(TypeError, 'not iterable'):
            h.update(1)

        with self.assertRaisesRegex(ValueError, 'map update sequence element'):
            h.update([(1, 2), (3, 4, 5)])

        with self.assertRaisesRegex(TypeError, 'cannot convert map update'):
            h.update([(1, 2), 1])

        self.assertEqual(dict(h.items()), {'a': 1, 'b': 2, 'z': 100})

    def test_map_mut_7(self):
        key = HashKey(123, 'aaa')

        h = self.Map({'a': 1, 'b': 2}, z=100)
        self.assertEqual(dict(h.items()), {'a': 1, 'b': 2, 'z': 100})

        upd = {key: 1}
        with HashKeyCrasher(error_on_hash=True):
            with self.assertRaises(HashingError):
                h.update(upd)

        upd = self.Map({key: 'zzz'})
        with HashKeyCrasher(error_on_hash=True):
            with self.assertRaises(HashingError):
                h.update(upd)

        upd = [(1, 2), (key, 'zzz')]
        with HashKeyCrasher(error_on_hash=True):
            with self.assertRaises(HashingError):
                h.update(upd)

        self.assertEqual(dict(h.items()), {'a': 1, 'b': 2, 'z': 100})

    def test_map_mut_8(self):
        key1 = HashKey(123, 'aaa')
        key2 = HashKey(123, 'bbb')

        h = self.Map({key1: 123})
        self.assertEqual(dict(h.items()), {key1: 123})

        upd = {key2: 1}
        with HashKeyCrasher(error_on_eq=True):
            with self.assertRaises(EqError):
                h.update(upd)

        upd = self.Map({key2: 'zzz'})
        with HashKeyCrasher(error_on_eq=True):
            with self.assertRaises(EqError):
                h.update(upd)

        upd = [(1, 2), (key2, 'zzz')]
        with HashKeyCrasher(error_on_eq=True):
            with self.assertRaises(EqError):
                h.update(upd)

        self.assertEqual(dict(h.items()), {key1: 123})

    def test_map_mut_9(self):
        key1 = HashKey(123, 'aaa')

        src = {key1: 123}
        with HashKeyCrasher(error_on_hash=True):
            with self.assertRaises(HashingError):
                self.Map(src)

        src = [(1, 2), (key1, 123)]
        with HashKeyCrasher(error_on_hash=True):
            with self.assertRaises(HashingError):
                self.Map(src)

    def test_map_mut_10(self):
        key1 = HashKey(123, 'aaa')

        m = self.Map({key1: 123})

        mm = m.mutate()
        with HashKeyCrasher(error_on_hash=True):
            with self.assertRaises(HashingError):
                del mm[key1]

        mm = m.mutate()
        with HashKeyCrasher(error_on_hash=True):
            with self.assertRaises(HashingError):
                mm.pop(key1, None)

        mm = m.mutate()
        with HashKeyCrasher(error_on_hash=True):
            with self.assertRaises(HashingError):
                mm.set(key1, 123)

    def test_map_mut_11(self):
        m = self.Map({'a': 1, 'b': 2})

        mm = m.mutate()
        self.assertEqual(mm.pop('a', 1), 1)
        self.assertEqual(mm.finish(), self.Map({'b': 2}))

        mm = m.mutate()
        self.assertEqual(mm.pop('b', 1), 2)
        self.assertEqual(mm.finish(), self.Map({'a': 1}))

        mm = m.mutate()
        self.assertEqual(mm.pop('b', 1), 2)
        del mm['a']
        self.assertEqual(mm.finish(), self.Map())

    def test_map_mut_12(self):
        m = self.Map({'a': 1, 'b': 2})

        mm = m.mutate()
        mm.finish()

        with self.assertRaisesRegex(ValueError, 'has been finished'):
            mm.pop('a')

        with self.assertRaisesRegex(ValueError, 'has been finished'):
            del mm['a']

        with self.assertRaisesRegex(ValueError, 'has been finished'):
            mm.set('a', 'b')

        with self.assertRaisesRegex(ValueError, 'has been finished'):
            mm['a'] = 'b'

        with self.assertRaisesRegex(ValueError, 'has been finished'):
            mm.update(a='b')

    def test_map_mut_13(self):
        key1 = HashKey(123, 'aaa')
        key2 = HashKey(123, 'aaa')

        m = self.Map({key1: 123})

        mm = m.mutate()
        with HashKeyCrasher(error_on_eq=True):
            with self.assertRaises(EqError):
                del mm[key2]

        mm = m.mutate()
        with HashKeyCrasher(error_on_eq=True):
            with self.assertRaises(EqError):
                mm.pop(key2, None)

        mm = m.mutate()
        with HashKeyCrasher(error_on_eq=True):
            with self.assertRaises(EqError):
                mm.set(key2, 123)

    def test_map_mut_14(self):
        m = self.Map(a=1, b=2)

        with m.mutate() as mm:
            mm['z'] = 100
            del mm['a']

        self.assertEqual(mm.finish(), self.Map(z=100, b=2))

    def test_map_mut_15(self):
        m = self.Map(a=1, b=2)

        with self.assertRaises(ZeroDivisionError):
            with m.mutate() as mm:
                mm['z'] = 100
                del mm['a']
                1 / 0

        self.assertEqual(mm.finish(), self.Map(z=100, b=2))
        self.assertEqual(m, self.Map(a=1, b=2))

    def test_map_mut_16(self):
        m = self.Map(a=1, b=2)
        hash(m)

        m2 = self.Map(m)
        m3 = self.Map(m, c=3)

        self.assertEqual(m, m2)
        self.assertEqual(len(m), len(m2))
        self.assertEqual(hash(m), hash(m2))

        self.assertIsNot(m, m2)
        self.assertEqual(m3, self.Map(a=1, b=2, c=3))

    def test_map_mut_17(self):
        m = self.Map(a=1)
        with m.mutate() as mm:
            with self.assertRaisesRegex(
                    TypeError, 'cannot create Maps from MapMutations'):
                self.Map(mm)

    def test_map_mut_18(self):
        m = self.Map(a=1, b=2)
        with m.mutate() as mm:
            mm.update(self.Map(x=1), z=2)
            mm.update(c=3)
            mm.update({'n': 100, 'a': 20})
            m2 = mm.finish()

        expected = self.Map(
            {'b': 2, 'c': 3, 'n': 100, 'z': 2, 'x': 1, 'a': 20})

        self.assertEqual(len(m2), 6)
        self.assertEqual(m2, expected)
        self.assertEqual(m, self.Map(a=1, b=2))

    def test_map_mut_19(self):
        m = self.Map(a=1, b=2)
        m2 = m.update({'a': 20})
        self.assertEqual(len(m2), 2)

    def test_map_mut_20(self):
        # Issue 24:

        h = self.Map()

        for i in range(19):
            # Create more than 16 keys to trigger the root bitmap
            # node to be converted into an array node
            h = h.set(HashKey(i, i), i)

        h = h.set(HashKey(18, '18-collision'), 18)

        with h.mutate() as m:
            del m[HashKey(18, 18)]
            del m[HashKey(18, '18-collision')]

            # The pre-issue-24 code failed to update the number of array
            # node element, so at this point it would be greater than it
            # actually is.
            h = m.finish()

        # Any of the below operations shouldn't crash the debug build.
        with h.mutate() as m:
            for i in range(18):
                del m[HashKey(i, i)]
            h = m.finish()
        h = h.set(HashKey(21, 21), 21)
        h = h.set(HashKey(22, 22), 22)

    def test_map_mut_21(self):
        # Issue 24:
        # Array nodes, while in mutation, failed to increment the
        # internal count of elements when adding a new key to it.
        # Because the internal count

        h = self.Map()

        for i in range(18):
            # Create more than 16 keys to trigger the root bitmap
            # node to be converted into an array node
            h = h.set(HashKey(i, i), i)

        with h.mutate() as m:
            # Add one new key to the array node
            m[HashKey(18, 18)] = 18
            # Add another key -- after this the old code failed
            # to increment the number of elements in the mutated
            # array node.
            m[HashKey(19, 19)] = 19
            h = m.finish()

        for i in range(20):
            # Start deleting keys one by one. Because array node
            # element count was accounted incorrectly (smaller by 1
            # than it actually is, the mutation for "del h[18]" would
            # create an empty array node, clipping the "19" key).
            # Before the issue #24 fix, the below line would crash
            # on i=19.
            h = h.delete(HashKey(i, i))

    def test_map_mut_stress(self):
        COLLECTION_SIZE = 7000
        TEST_ITERS_EVERY = 647
        RUN_XTIMES = 3

        for _ in range(RUN_XTIMES):
            h = self.Map()
            d = dict()

            for i in range(COLLECTION_SIZE // TEST_ITERS_EVERY):

                hm = h.mutate()
                for j in range(TEST_ITERS_EVERY):
                    key = random.randint(1, 100000)
                    key = HashKey(key % 271, str(key))

                    hm.set(key, key)
                    d[key] = key

                    self.assertEqual(len(hm), len(d))

                h2 = hm.finish()
                self.assertEqual(dict(h2.items()), d)
                h = h2

            self.assertEqual(dict(h.items()), d)
            self.assertEqual(len(h), len(d))

            it = iter(tuple(d.keys()))
            for i in range(COLLECTION_SIZE // TEST_ITERS_EVERY):

                hm = h.mutate()
                for j in range(TEST_ITERS_EVERY):
                    try:
                        key = next(it)
                    except StopIteration:
                        break

                    del d[key]
                    del hm[key]

                    self.assertEqual(len(hm), len(d))

                h2 = hm.finish()
                self.assertEqual(dict(h2.items()), d)
                h = h2

            self.assertEqual(dict(h.items()), d)
            self.assertEqual(len(h), len(d))

    def test_map_pickle(self):
        h = self.Map(a=1, b=2)
        for proto in range(pickle.HIGHEST_PROTOCOL):
            p = pickle.dumps(h, proto)
            uh = pickle.loads(p)

            self.assertTrue(isinstance(uh, self.Map))
            self.assertEqual(h, uh)

        with self.assertRaisesRegex(TypeError, "can('t|not) pickle"):
            pickle.dumps(h.mutate())

    @unittest.skipIf(
        sys.version_info < (3, 7, 0), "__class_getitem__ is not available"
    )
    def test_map_is_subscriptable(self):
        self.assertIs(self.Map[int, str], self.Map)

    def test_kwarg_named_col(self):
        self.assertEqual(dict(self.Map(col=0)), {"col": 0})
        self.assertEqual(dict(self.Map(a=0, col=1)), {"a": 0, "col": 1})
        self.assertEqual(dict(self.Map({"a": 0}, col=1)), {"a": 0, "col": 1})


class PyMapTest(BaseMapTest, unittest.TestCase):

    Map = PyMap


try:
    from immutables._map import Map as CMap
except ImportError:
    CMap = None


@unittest.skipIf(CMap is None, 'C Map is not available')
class CMapTest(BaseMapTest, unittest.TestCase):

    Map = CMap


if __name__ == "__main__":
    unittest.main()
