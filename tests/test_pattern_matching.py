import sys
import textwrap
import unittest

from immutables.map import Map as PyMap


class BaseMapTest:

    Map = None

    @unittest.skipIf(
        sys.version_info < (3, 10),
        "pattern matching is not supported in this Python version",
    )
    def test_map_can_be_matched(self):
        locals_ = dict(locals())
        exec(
            textwrap.dedent("""\
            match self.Map(a=1, b=2):  # noqa: E999
                case {"a": 1 as matched}:
                    matched = matched
                case _:
                    assert False

            self.assertEqual(matched, 1)
            """),
            globals(),
            locals_,
        )


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
