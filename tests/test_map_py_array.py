import unittest

from immutables.map_with_array_nodes import Map as PyAMap
from tests.test_map import BaseMapTest


class PyAMapTest(BaseMapTest, unittest.TestCase):
    Map = PyAMap

    def test_map_stress(self):
        pass

    def test_map_mut_stress(self):
        pass


if __name__ == '__main__':
    unittest.main()
