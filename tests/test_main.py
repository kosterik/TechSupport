"""Модульные тесты для проверки запуска приложения."""

import io
import os
import sys
import unittest
from unittest.mock import patch

# Добавление путей к модулям
_current_dir = os.path.dirname(__file__)
_src_dir = os.path.abspath(os.path.join(_current_dir, "..", "src"))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

try:
    from techsupport.main import main
except ImportError:
    from src.techsupport.main import main


class TestTechSupportMain(unittest.TestCase):
    """Тестирование точки входа программы."""

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_output(self, mock_stdout):
        """Проверка стандартного вывода программы."""
        main()
        self.assertEqual(mock_stdout.getvalue().strip(), "hello world")


if __name__ == "__main__":
    unittest.main()
