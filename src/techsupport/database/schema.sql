PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS ticket_tags;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS statuses;
DROP TABLE IF EXISTS priorities;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE priorities (
    priority_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    level INTEGER NOT NULL UNIQUE
);

CREATE TABLE statuses (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
    FOREIGN KEY (role_id) REFERENCES roles (role_id) ON DELETE RESTRICT
);

CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,
    phone TEXT,
    department TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    client_id INTEGER NOT NULL,
    assignee_id INTEGER,
    category_id INTEGER NOT NULL,
    priority_id INTEGER NOT NULL,
    status_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
    updated_at TEXT NOT NULL DEFAULT (DATETIME('now')),
    FOREIGN KEY (client_id) REFERENCES users (user_id) ON DELETE RESTRICT,
    FOREIGN KEY (assignee_id) REFERENCES users (user_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES categories (category_id) ON DELETE RESTRICT,
    FOREIGN KEY (priority_id) REFERENCES priorities (priority_id) ON DELETE RESTRICT,
    FOREIGN KEY (status_id) REFERENCES statuses (status_id) ON DELETE RESTRICT
);

CREATE TABLE ticket_tags (
    ticket_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (ticket_id, tag_id),
    FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE
);

INSERT INTO roles (role_id, name, description) VALUES
    (1, 'Администратор', 'Сотрудник службы поддержки с полными правами управления заявками'),
    (2, 'Пользователь', 'Клиент системы, регистрирующий и отслеживающий обращения');

INSERT INTO categories (category_id, name, description) VALUES
    (1, 'Оборудование', 'Неполадки с ПК, мониторами, принтерами и периферией'),
    (2, 'Программное обеспечение', 'Ошибки в корпоративном ПО, установка и обновление программ'),
    (3, 'Сетевые проблемы', 'Проблемы с доступом к локальной сети, интернет, VPN'),
    (4, 'Учётные записи и доступ', 'Сброс паролей, выдача прав доступа к ресурсам');

INSERT INTO priorities (priority_id, name, level) VALUES
    (1, 'Низкий', 1),
    (2, 'Средний', 2),
    (3, 'Высокий', 3),
    (4, 'Критический', 4);

INSERT INTO statuses (status_id, name, description) VALUES
    (1, 'Новая', 'Заявка зарегистрирована и ожидает назначения исполнителя'),
    (2, 'В работе', 'Исполнитель назначен, ведутся работы по устранению'),
    (3, 'Ожидает ответа', 'Требуются уточняющие данные от пользователя'),
    (4, 'Закрыта', 'Проблема решена, обращение успешно закрыто'),
    (5, 'Отклонена', 'Заявка отклонена администратором с указанием причины');

INSERT INTO tags (tag_id, name) VALUES
    (1, 'Срочно'),
    (2, 'ПО'),
    (3, 'ПК'),
    (4, 'Принтер'),
    (5, 'VPN');

INSERT INTO users (user_id, login, password_hash, full_name, role_id, created_at) VALUES
    (1, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Иванов Иван Иванович', 1, '2026-10-01 09:00:00'),
    (2, 'petrov', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'Петров Петр Петрович', 2, '2026-10-02 10:15:00'),
    (3, 'sidorova', '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5', 'Сидорова Анна Сергеевна', 2, '2026-10-03 11:30:00');

INSERT INTO user_profiles (user_id, email, phone, department) VALUES
    (1, 'admin@techsupport.local', '+7 (999) 000-00-01', 'ИТ-отдел'),
    (2, 'petrov@corp.local', '+7 (999) 111-22-33', 'Бухгалтерия'),
    (3, 'sidorova@corp.local', '+7 (999) 222-33-44', 'Отдел кадров');

INSERT INTO tickets (ticket_id, title, description, client_id, assignee_id, category_id, priority_id, status_id, created_at, updated_at) VALUES
    (1, 'Не включается системный блок', 'При нажатии на кнопку питания компьютер не реагирует, кулеры не крутятся.', 2, 1, 1, 3, 2, '2026-10-10 10:00:00', '2026-10-10 10:30:00'),
    (2, 'Ошибка формирования отчета в 1С', 'При попытке выгрузить расчетную ведомость приложение аварийно завершает работу.', 2, 1, 2, 2, 1, '2026-10-12 14:20:00', '2026-10-12 14:20:00'),
    (3, 'Сброс пароля от корпоративной почты', 'Заблокировалась учетная запись после трёх неверных попыток ввода пароля.', 3, NULL, 4, 2, 1, '2026-10-15 08:45:00', '2026-10-15 08:45:00');

INSERT INTO ticket_tags (ticket_id, tag_id) VALUES
    (1, 1),
    (1, 3),
    (2, 2),
    (3, 1);
