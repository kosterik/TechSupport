from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict, List, Optional


DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "techsupport.db")
)
DEFAULT_SCHEMA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "schema.sql")
)


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(
    db_path: str = DEFAULT_DB_PATH,
    schema_path: Optional[str] = None,
) -> None:
    if schema_path is None:
        schema_path = DEFAULT_SCHEMA_PATH

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Файл схемы не найден: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


def get_all_roles(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    cursor = conn.execute("SELECT role_id, name, description FROM roles ORDER BY role_id;")
    return cursor.fetchall()


def get_all_categories(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    cursor = conn.execute("SELECT category_id, name, description FROM categories ORDER BY category_id;")
    return cursor.fetchall()


def get_all_priorities(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    cursor = conn.execute("SELECT priority_id, name, level FROM priorities ORDER BY level;")
    return cursor.fetchall()


def get_all_statuses(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    cursor = conn.execute("SELECT status_id, name, description FROM statuses ORDER BY status_id;")
    return cursor.fetchall()


def get_user_by_login(conn: sqlite3.Connection, login: str) -> Optional[sqlite3.Row]:
    cursor = conn.execute(
        """
        SELECT u.user_id, u.login, u.password_hash, u.full_name, u.role_id,
               r.name AS role_name, p.email, p.phone, p.department
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        LEFT JOIN user_profiles p ON u.user_id = p.user_id
        WHERE u.login = ?;
        """,
        (login,),
    )
    return cursor.fetchone()


def create_user(
    conn: sqlite3.Connection,
    login: str,
    password_hash: str,
    full_name: str,
    role_id: int = 2,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    department: Optional[str] = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO users (login, password_hash, full_name, role_id)
        VALUES (?, ?, ?, ?);
        """,
        (login, password_hash, full_name, role_id),
    )
    if cursor.lastrowid is None:
        raise RuntimeError("Не удалось получить id созданного пользователя")
    user_id = cursor.lastrowid

    if email or phone or department:
        conn.execute(
            """
            INSERT INTO user_profiles (user_id, email, phone, department)
            VALUES (?, ?, ?, ?);
            """,
            (user_id, email, phone, department),
        )

    conn.commit()
    return user_id


def create_ticket(
    conn: sqlite3.Connection,
    title: str,
    description: str,
    client_id: int,
    category_id: int,
    priority_id: int,
    tag_ids: Optional[List[int]] = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO tickets (title, description, client_id, category_id, priority_id, status_id)
        VALUES (?, ?, ?, ?, ?, 1);
        """,
        (title, description, client_id, category_id, priority_id),
    )
    if cursor.lastrowid is None:
        raise RuntimeError("Не удалось получить id созданной заявки")
    ticket_id = cursor.lastrowid

    if tag_ids:
        for tag_id in tag_ids:
            conn.execute(
                """
                INSERT INTO ticket_tags (ticket_id, tag_id)
                VALUES (?, ?);
                """,
                (ticket_id, tag_id),
            )

    conn.commit()
    return ticket_id


def get_ticket_details(conn: sqlite3.Connection, ticket_id: int) -> Optional[Dict[str, Any]]:
    cursor = conn.execute(
        """
        SELECT 
            t.ticket_id,
            t.title,
            t.description,
            t.created_at,
            t.updated_at,
            client.user_id AS client_id,
            client.full_name AS client_name,
            assignee.user_id AS assignee_id,
            assignee.full_name AS assignee_name,
            c.name AS category_name,
            p.name AS priority_name,
            p.level AS priority_level,
            s.name AS status_name
        FROM tickets t
        JOIN users client ON t.client_id = client.user_id
        LEFT JOIN users assignee ON t.assignee_id = assignee.user_id
        JOIN categories c ON t.category_id = c.category_id
        JOIN priorities p ON t.priority_id = p.priority_id
        JOIN statuses s ON t.status_id = s.status_id
        WHERE t.ticket_id = ?;
        """,
        (ticket_id,),
    )
    row = cursor.fetchone()
    if not row:
        return None

    ticket = dict(row)

    tags_cursor = conn.execute(
        """
        SELECT tg.name
        FROM ticket_tags tt
        JOIN tags tg ON tt.tag_id = tg.tag_id
        WHERE tt.ticket_id = ?
        ORDER BY tg.name;
        """,
        (ticket_id,),
    )
    ticket["tags"] = [r["name"] for r in tags_cursor.fetchall()]
    return ticket


def get_all_tickets(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.execute(
        """
        SELECT 
            t.ticket_id,
            t.title,
            client.full_name AS client_name,
            c.name AS category_name,
            p.name AS priority_name,
            s.name AS status_name,
            t.created_at
        FROM tickets t
        JOIN users client ON t.client_id = client.user_id
        JOIN categories c ON t.category_id = c.category_id
        JOIN priorities p ON t.priority_id = p.priority_id
        JOIN statuses s ON t.status_id = s.status_id
        ORDER BY t.ticket_id DESC;
        """
    )
    return [dict(r) for r in cursor.fetchall()]
