import os
import mypy.test.testcmdline
from mypy.test.helpers import normalize_error_messages


# I'm upset. There's no other way to deal with the little 'defined here'
# notes that mypy emits when passing an unexpected keyword argument
# and at no other time.
def renormalize_error_messages(messages):
    messages = [x for x in messages if not x.endswith(' defined here')]
    return normalize_error_messages(messages)


mypy.test.testcmdline.normalize_error_messages = renormalize_error_messages


this_file_dir = os.path.dirname(os.path.realpath(__file__))
test_data_prefix = os.path.join(this_file_dir, 'test-data')


class ImmuMypyTest(mypy.test.testcmdline.PythonCmdlineSuite):
    data_prefix = test_data_prefix
    files = ['check-immu.test']
