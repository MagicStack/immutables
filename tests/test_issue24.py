import unittest

from immutables.map import Map as PyMap, map_bitcount


class CollisionKey:
    def __hash__(self):
        return 0


class Issue24Base:
    Map = None

    def test_issue24(self):
        keys = range(27)
        new_entries = dict.fromkeys(keys, True)
        m = self.Map(new_entries)
        self.assertTrue(17 in m)
        with m.mutate() as mm:
            for i in keys:
                del mm[i]
            self.assertEqual(len(mm), 0)

    def dump_check_node_kind(self, header, kind):
        header = header.strip()
        self.assertTrue(header.strip().startswith(kind))

    def dump_check_node_size(self, header, size):
        node_size = header.split('size=', 1)[1]
        node_size = int(node_size.split(maxsplit=1)[0])
        self.assertEqual(node_size, size)

    def dump_check_bitmap_count(self, header, count):
        header = header.split('bitmap=')[1]
        bitmap = int(header.split(maxsplit=1)[0], 0)
        self.assertEqual(map_bitcount(bitmap), count)

    def dump_check_bitmap_node_count(self, header, count):
        self.dump_check_node_kind(header, 'Bitmap')
        self.dump_check_node_size(header, count * 2)
        self.dump_check_bitmap_count(header, count)

    def dump_check_collision_node_count(self, header, count):
        self.dump_check_node_kind(header, 'Collision')
        self.dump_check_node_size(header, 2 * count)

    def test_bitmap_node_update_in_place_count(self):
        keys = range(7)
        new_entries = dict.fromkeys(keys, True)
        m = self.Map(new_entries)
        d = m.__dump__().splitlines()
        self.assertTrue(d)
        if d[0].startswith('HAMT'):
            header = d[1]  # skip _map.Map.__dump__() header
        else:
            header = d[0]
        self.dump_check_bitmap_node_count(header, 7)

    def test_bitmap_node_delete_in_place_count(self):
        keys = range(7)
        new_entries = dict.fromkeys(keys, True)
        m = self.Map(new_entries)
        with m.mutate() as mm:
            del mm[0], mm[2], mm[3]
            m2 = mm.finish()
        d = m2.__dump__().splitlines()
        self.assertTrue(d)
        if d[0].startswith('HAMT'):
            header = d[1]  # skip _map.Map.__dump__() header
        else:
            header = d[0]
        self.dump_check_bitmap_node_count(header, 4)

    def test_collision_node_update_in_place_count(self):
        keys = (CollisionKey() for i in range(7))
        new_entries = dict.fromkeys(keys, True)
        m = self.Map(new_entries)
        d = m.__dump__().splitlines()
        self.assertTrue(len(d) > 3)
        # get node headers
        if d[0].startswith('HAMT'):
            h1, h2 = d[1], d[3]  # skip _map.Map.__dump__() header
        else:
            h1, h2 = d[0], d[2]
        self.dump_check_node_kind(h1, 'Bitmap')
        self.dump_check_collision_node_count(h2, 7)

    def test_collision_node_delete_in_place_count(self):
        keys = [CollisionKey() for i in range(7)]
        new_entries = dict.fromkeys(keys, True)
        m = self.Map(new_entries)
        with m.mutate() as mm:
            del mm[keys[0]], mm[keys[2]], mm[keys[3]]
            m2 = mm.finish()
        d = m2.__dump__().splitlines()
        self.assertTrue(len(d) > 3)
        # get node headers
        if d[0].startswith('HAMT'):
            h1, h2 = d[1], d[3]  # skip _map.Map.__dump__() header
        else:
            h1, h2 = d[0], d[2]
        self.dump_check_node_kind(h1, 'Bitmap')
        self.dump_check_collision_node_count(h2, 4)


try:
    from immutables._map import Map as CMap
except ImportError:
    CMap = None


class Issue24PyTest(Issue24Base, unittest.TestCase):
    Map = PyMap


@unittest.skipIf(CMap is None, 'C Map is not available')
class Issue24CTest(Issue24Base, unittest.TestCase):
    Map = CMap

    def hamt_dump_check_first_return_second(self, m):
        d = m.__dump__().splitlines()
        self.assertTrue(len(d) > 2)
        self.assertTrue(d[0].startswith('HAMT'))
        return d[1]

    def test_array_node_update_in_place_count(self):
        keys = range(27)
        new_entries = dict.fromkeys(keys, True)
        m = self.Map(new_entries)
        header = self.hamt_dump_check_first_return_second(m)
        self.dump_check_node_kind(header, 'Array')
        for i in range(2, 18):
            m = m.delete(i)
        header = self.hamt_dump_check_first_return_second(m)
        self.dump_check_bitmap_node_count(header, 11)

    def test_array_node_delete_in_place_count(self):
        keys = range(27)
        new_entries = dict.fromkeys(keys, True)
        m = self.Map(new_entries)
        header = self.hamt_dump_check_first_return_second(m)
        self.dump_check_node_kind(header, 'Array')
        with m.mutate() as mm:
            for i in range(5):
                del mm[i]
            m2 = mm.finish()
        header = self.hamt_dump_check_first_return_second(m2)
        self.dump_check_node_kind(header, 'Array')
        for i in range(6, 17):
            m2 = m2.delete(i)
        header = self.hamt_dump_check_first_return_second(m2)
        self.dump_check_bitmap_node_count(header, 11)


if __name__ == '__main__':
    unittest.main()
