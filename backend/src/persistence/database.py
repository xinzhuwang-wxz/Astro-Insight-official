from pathlib import Path
import sqlite3

DB = Path("astro_insight_runtime.db")

def connect():
    return sqlite3.connect(DB)

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS llm_configs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT,
        model TEXT,
        base_url TEXT,
        api_key TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usage_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT,
        tokens INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()