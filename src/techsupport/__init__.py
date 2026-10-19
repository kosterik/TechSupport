"""Пакет приложения TechSupport."""

from techsupport.database import get_connection, init_db

__version__ = "1.0.0"
__all__ = ["get_connection", "init_db", "__version__"]
