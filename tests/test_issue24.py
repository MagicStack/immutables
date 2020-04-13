import unittest


from immutables.map import Map as PyMap


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


try:
    from immutables._map import Map as CMap
except ImportError:
    CMap = None


class Issue24PyTest(Issue24Base, unittest.TestCase):
    Map = PyMap


class Issue24CTest(Issue24Base, unittest.TestCase):
    Map = CMap


if __name__ == '__main__':
    unittest.main()
