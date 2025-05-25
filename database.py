import sqlite3

DB_PATH = 'data/donnees.db'

def connect_db():
    return sqlite3.connect(DB_PATH)

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        userId INTEGER,
        title TEXT,
        body TEXT
    )''')
    conn.commit()
    conn.close()

def clear_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts")
    conn.commit()
    conn.close()

def insert_data(data):
    conn = connect_db()
    cursor = conn.cursor()
    for item in data:
        cursor.execute("INSERT INTO posts (id, userId, title, body) VALUES (?, ?, ?, ?)",
                       (item['id'], item['userId'], item['title'], item['body']))
    conn.commit()
    conn.close()

def fetch_all():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    rows = cursor.fetchall()
    conn.close()
    return rows