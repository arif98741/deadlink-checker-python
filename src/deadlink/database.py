import sqlite3
import os
from datetime import datetime
from .models import LinkResult

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Place database in the parent directory of the current file's package
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "deadlink_history.db")
        
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    mode TEXT,
                    total_links INTEGER,
                    working_links INTEGER,
                    broken_links INTEGER,
                    session_folder TEXT
                )
            """)
            # Results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    url TEXT NOT NULL,
                    status_code INTEGER,
                    status_text TEXT,
                    response_time REAL,
                    found_on TEXT,
                    is_dead BOOLEAN,
                    is_external BOOLEAN,
                    link_type TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def save_session(self, url, mode, results, session_folder):
        total = len(results)
        broken = len([r for r in results if r.is_dead])
        working = total - broken
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (url, mode, total_links, working_links, broken_links, session_folder)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (url, mode, total, working, broken, session_folder))
            
            session_id = cursor.lastrowid
            
            for r in results:
                cursor.execute("""
                    INSERT INTO results (session_id, url, status_code, status_text, response_time, found_on, is_dead, is_external, link_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id, r.url, r.status_code, r.status_text, 
                    r.response_time, r.found_on, int(r.is_dead), 
                    int(r.is_external), r.link_type
                ))
            conn.commit()
            return session_id

    def get_sessions(self, search_query=None):
        query = "SELECT * FROM sessions"
        params = []
        if search_query:
            query += " WHERE url LIKE ? OR timestamp LIKE ?"
            params = [f"%{search_query}%", f"%{search_query}%"]
        
        query += " ORDER BY timestamp DESC"
        
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_session_results(self, session_id):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM results WHERE session_id = ?", (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_session(self, session_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
