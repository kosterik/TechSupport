import io
import sys
import unittest
from unittest.mock import patch

# Ensure src is on sys.path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from techsupport.main import main


class TestTechSupportMain(unittest.TestCase):
    """Тестирование точки входа программы."""

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_output(self, mock_stdout):
        main()
        self.assertEqual(mock_stdout.getvalue().strip(), "hello world")


if __name__ == "__main__":
    unittest.main()
