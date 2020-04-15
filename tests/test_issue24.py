import unittest


from immutables.map import Map as PyMap
from immutables.map_with_array_nodes import Map as PyAMap
from tests.test_map import BaseMapTest#, PyMapTest, CMapTest


class Issue24Base:
    Map = None

    def test_issue24(self):
        keys = range(27)
        new_entries = dict.fromkeys(keys, True)
        m = self.Map(new_entries)
        self.assertTrue(17 in m)
        if self.crasher:
            with m.mutate() as mm, self.assertRaises(KeyError):
                for i in keys:
                    del mm[i]
                #self.assertEqual(len(mm), 0)
        else:
            with m.mutate() as mm:
                for i in keys:
                    del mm[i]
                #self.assertEqual(len(mm), 0)


try:
    from immutables._map import Map as CMap
except ImportError:
    CMap = None


class Issue24PyTest(Issue24Base, unittest.TestCase):
    Map = PyMap
    crasher = False


@unittest.skipIf(CMap is None, 'C Map is not available')
class Issue24CTest(Issue24Base, unittest.TestCase):
    Map = CMap
    crasher = True


class Issue24ArrayTest(Issue24Base, unittest.TestCase):
    Map = PyAMap
    crasher = False


if __name__ == '__main__':
    unittest.main()
