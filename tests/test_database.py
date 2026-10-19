import os
import sqlite3
import sys
import tempfile
import unittest

_current_dir = os.path.dirname(__file__)
_src_dir = os.path.abspath(os.path.join(_current_dir, "..", "src"))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from techsupport.database import (
    create_ticket,
    create_user,
    get_all_categories,
    get_all_priorities,
    get_all_roles,
    get_all_statuses,
    get_all_tickets,
    get_connection,
    get_ticket_details,
    get_user_by_login,
    init_db,
)


class TestTechSupportDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(self.db_path)
        self.conn = get_connection(self.db_path)

    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def test_tables_created(self):
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )
        tables = {row["name"] for row in cursor.fetchall()}
        expected_tables = {
            "roles",
            "categories",
            "priorities",
            "statuses",
            "users",
            "user_profiles",
            "tickets",
            "tags",
            "ticket_tags",
        }
        self.assertTrue(expected_tables.issubset(tables))

    def test_seed_data_loaded(self):
        roles = get_all_roles(self.conn)
        self.assertGreaterEqual(len(roles), 2)

        categories = get_all_categories(self.conn)
        self.assertGreaterEqual(len(categories), 4)

        priorities = get_all_priorities(self.conn)
        self.assertGreaterEqual(len(priorities), 4)

        statuses = get_all_statuses(self.conn)
        self.assertGreaterEqual(len(statuses), 5)

        tickets = get_all_tickets(self.conn)
        self.assertGreaterEqual(len(tickets), 3)

    def test_foreign_key_constraint(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO users (login, password_hash, full_name, role_id) VALUES (?, ?, ?, ?);",
                ("bad_user", "hash", "Тестовый Тест", 999),
            )

    def test_unique_constraint(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO users (login, password_hash, full_name, role_id) VALUES (?, ?, ?, ?);",
                ("admin", "another_hash", "Дубликат", 1),
            )

    def test_one_to_one_relationship(self):
        user = get_user_by_login(self.conn, "petrov")
        self.assertIsNotNone(user)
        self.assertEqual(user["department"], "Бухгалтерия")

        uid = create_user(
            self.conn,
            login="temp_user",
            password_hash="temp_hash",
            full_name="Временный Пользователь",
            role_id=2,
            email="temp@corp.local",
            department="Склад",
        )
        profile_row = self.conn.execute(
            "SELECT * FROM user_profiles WHERE user_id = ?;", (uid,)
        ).fetchone()
        self.assertIsNotNone(profile_row)

        self.conn.execute("DELETE FROM users WHERE user_id = ?;", (uid,))
        self.conn.commit()
        profile_after = self.conn.execute(
            "SELECT * FROM user_profiles WHERE user_id = ?;", (uid,)
        ).fetchone()
        self.assertIsNone(profile_after)

    def test_many_to_many_relationship(self):
        ticket = get_ticket_details(self.conn, 1)
        self.assertIsNotNone(ticket)
        self.assertIn("Срочно", ticket["tags"])
        self.assertIn("ПК", ticket["tags"])

    def test_create_ticket_and_details(self):
        new_ticket_id = create_ticket(
            self.conn,
            title="Проблема с принтером",
            description="Замятие бумаги в лотке №2",
            client_id=2,
            category_id=1,
            priority_id=2,
            tag_ids=[1, 4],
        )
        self.assertGreater(new_ticket_id, 0)

        details = get_ticket_details(self.conn, new_ticket_id)
        self.assertIsNotNone(details)
        self.assertEqual(details["title"], "Проблема с принтером")
        self.assertEqual(details["category_name"], "Оборудование")
        self.assertEqual(details["status_name"], "Новая")
        self.assertListEqual(sorted(details["tags"]), ["Принтер", "Срочно"])


if __name__ == "__main__":
    unittest.main()
