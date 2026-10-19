import io
import os
import sys
import unittest
from unittest.mock import patch

_current_dir = os.path.dirname(__file__)
_src_dir = os.path.abspath(os.path.join(_current_dir, "..", "src"))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

try:
    from techsupport.main import main  # type: ignore[import-not-found, missing-import]
except ImportError:
    from src.techsupport.main import main  # type: ignore[import-not-found, missing-import]


class TestTechSupportMain(unittest.TestCase):

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_output(self, mock_stdout):
        main()
        self.assertEqual(mock_stdout.getvalue().strip(), "hello world")


if __name__ == "__main__":
    unittest.main()
