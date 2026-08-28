import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    policy_number TEXT UNIQUE NOT NULL,
    policy_type TEXT NOT NULL,
    coverage_amount REAL NOT NULL,
    status TEXT DEFAULT 'Active',
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    policy_id INTEGER NOT NULL,
    claim_amount REAL NOT NULL,
    reason TEXT NOT NULL,
    claim_date TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

admin_password = generate_password_hash("admin123")

cursor.execute("""
INSERT OR IGNORE INTO users
(name, email, password, role)
VALUES (?, ?, ?, ?)
""", (
    "Admin",
    "admin@gmail.com",
    admin_password,
    "admin"
))

cursor.execute("""
UPDATE users
SET password = ?, role = 'admin'
WHERE email = 'admin@gmail.com'
""", (admin_password,))

connection.commit()
connection.close()

print("Database created successfully!")