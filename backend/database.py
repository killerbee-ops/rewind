import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rewind.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        tag TEXT NOT NULL,
        time_of_day TEXT NOT NULL,
        hour_of_day INTEGER DEFAULT 12,
        intensity INTEGER DEFAULT 3,
        context TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        tag TEXT NOT NULL,
        planned_time TEXT NOT NULL,
        planned_hour INTEGER DEFAULT 20,
        status TEXT DEFAULT 'Pending',
        warning_triggered INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        todo_id INTEGER,
        regret_id INTEGER,
        score REAL,
        match_reasons TEXT,
        warning_shown INTEGER DEFAULT 1,
        user_action TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (todo_id) REFERENCES todos (id),
        FOREIGN KEY (regret_id) REFERENCES regrets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag TEXT,
        title TEXT NOT NULL,
        frequency INTEGER DEFAULT 1,
        context_summary TEXT,
        explanation TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
