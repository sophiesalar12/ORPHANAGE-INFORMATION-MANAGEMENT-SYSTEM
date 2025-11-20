import sqlite3
from werkzeug.security import generate_password_hash
import os

# USE THE EXACT SAME DB PATH AS app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'orphanage.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# Create table if it doesn't exist
conn.execute('''
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

# Admin credentials
username = "admin"
password = "admin123"

# Hash password
password_hash = generate_password_hash(password)

# Check if user exists
admin = conn.execute(
    'SELECT * FROM admins WHERE username = ?',
    (username,)
).fetchone()

if admin:
    print(f"Admin '{username}' already exists.")
else:
    conn.execute(
        'INSERT INTO admins (username, password_hash) VALUES (?, ?)',
        (username, password_hash)
    )
    conn.commit()
    print(f"Admin '{username}' created successfully with password '{password}'")

conn.close()
