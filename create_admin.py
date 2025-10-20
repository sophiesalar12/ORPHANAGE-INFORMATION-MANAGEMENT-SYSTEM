import sqlite3
from werkzeug.security import generate_password_hash


conn = sqlite3.connect('orphanage.db')
conn.row_factory = sqlite3.Row


conn.execute('''
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
)
''')


username = 'admin'
password = 'admin123'
password_hash = generate_password_hash(password)


admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()

if admin:
    print(f"Admin user '{username}' already exists.")
else:
    conn.execute('INSERT INTO admins (username, password_hash) VALUES (?, ?)', 
                (username, password_hash))
    conn.commit()
    print(f"Admin user '{username}' created successfully with password '{password}'.")

conn.close()