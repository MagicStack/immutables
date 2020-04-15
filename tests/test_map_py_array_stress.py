import unittest

from immutables.map_with_array_nodes import Map as PyAMap
from tests.test_map import BaseMapTest


class PyAMapTest(unittest.TestCase):
    Map = PyAMap

    test_map_stress = BaseMapTest.test_map_stress
    test_map_mut_stress = BaseMapTest.test_map_mut_stress


if __name__ == '__main__':
    unittest.main()
