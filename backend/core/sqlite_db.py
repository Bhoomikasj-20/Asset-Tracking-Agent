import sqlite3

class SQLiteDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._init_tables()

    def _init_tables(self):
        """Initialize the assets table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY,
                asset_type TEXT,
                brand TEXT,
                model_number TEXT,
                assigned_to TEXT,
                purchase_date TEXT,
                status TEXT,
                last_updated_at TEXT
            );
        """)
        self.conn.commit()

    def execute(self, query, params=(), fetchone=False, fetchall=False):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
        return None


# ✅ Initialize the DB instance once
db = SQLiteDB("assets.db")
