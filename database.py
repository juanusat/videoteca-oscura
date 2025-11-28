import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.path.join('instance', 'database.db')

def init_database():
    os.makedirs('instance', exist_ok=True)
    
    schema_path = os.path.join('setup', 'schema_database.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.executescript(schema)
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
            return cursor.lastrowid
        
        if fetch_one:
            return cursor.fetchone()
        
        if fetch_all:
            return cursor.fetchall()
        
        return None
