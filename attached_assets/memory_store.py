import sqlite3

def init_db():
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            user_id TEXT,
            key TEXT,
            value TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_memory(user_id, key, value):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("INSERT INTO memory (user_id, key, value) VALUES (?, ?, ?)", (user_id, key, value))
    conn.commit()
    conn.close()

def get_memory(user_id, key):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("SELECT value FROM memory WHERE user_id = ? AND key = ? ORDER BY timestamp DESC LIMIT 1", (user_id, key))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None