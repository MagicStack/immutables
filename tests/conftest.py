# We need the mypy pytest plugin to do the test collection for our
# typing tests.

# mypy demands that its test-data be present for mypy.test.config to be
# imported, so thwart that check. mypy PR #10919 fixes this.
import unittest.mock
with unittest.mock.patch('os.path.isdir') as isdir:
    isdir.return_value = True
    import mypy.test.config  # noqa

pytest_plugins = [
    'mypy.test.data',
]
