"""Модульные тесты для проверки запуска приложения."""

import io
import os
import sys
import unittest
from unittest.mock import patch

# Добавление каталога src в пути поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from techsupport.main import main


class TestTechSupportMain(unittest.TestCase):
    """Тестирование точки входа программы."""

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_output(self, mock_stdout):
        """Проверка стандартного вывода программы."""
        main()
        self.assertEqual(mock_stdout.getvalue().strip(), "hello world")


if __name__ == "__main__":
    unittest.main()
