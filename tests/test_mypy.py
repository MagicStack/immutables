import os
import re

try:
    import mypy.test.testcmdline
    from mypy.test.helpers import normalize_error_messages
except (ImportError, AssertionError):
    if os.environ.get('IMMU_SKIP_MYPY_TESTS'):
        pass
    else:
        raise
else:
    # I'm upset. There's no other way to deal with the little 'defined here'
    # (or, in newer mypy, 'defined in "module"') notes that mypy emits when
    # passing an unexpected keyword argument and at no other time.
    _defined_note = re.compile(r'note: .* defined (here|in "[^"]+")$')

    def renormalize_error_messages(messages):
        messages = [x for x in messages if not _defined_note.search(x)]
        return normalize_error_messages(messages)

    mypy.test.testcmdline.normalize_error_messages = renormalize_error_messages

    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    test_data_prefix = os.path.join(this_file_dir, 'test-data')
    parent_dir = os.path.dirname(this_file_dir)

    mypy_path = os.environ.get("MYPYPATH")
    if mypy_path:
        mypy_path = parent_dir + os.pathsep + mypy_path
    else:
        mypy_path = parent_dir

    class ImmuMypyTest(mypy.test.testcmdline.PythonCmdlineSuite):
        data_prefix = test_data_prefix
        files = ['check-immu.test']

        def run_case(self, testcase):
            os.environ["MYPYPATH"] = mypy_path
            super().run_case(testcase)
