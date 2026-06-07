import sqlite3
import os

class SQLiteDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._init_tables()

    def _init_tables(self):
        """Initialize the assets and audit_logs tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY,
                asset_name TEXT DEFAULT '',
                asset_type TEXT,
                category TEXT DEFAULT 'General',
                brand TEXT,
                model_number TEXT,
                assigned_to TEXT,
                purchase_date TEXT,
                warranty_expiry TEXT DEFAULT '',
                location TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                status TEXT,
                last_updated_at TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id TEXT PRIMARY KEY,
                asset_id TEXT,
                action TEXT,
                performed_by TEXT DEFAULT 'System',
                details TEXT DEFAULT '',
                timestamp TEXT
            );
        """)
        self.conn.commit()
        # Migrate existing tables to add new columns if needed
        self._migrate_tables()

    def _migrate_tables(self):
        """Add new columns to existing tables if they don't exist."""
        cursor = self.conn.cursor()
        existing_columns = [row[1] for row in cursor.execute("PRAGMA table_info(assets)").fetchall()]
        new_columns = {
            'asset_name': "TEXT DEFAULT ''",
            'category': "TEXT DEFAULT 'General'",
            'warranty_expiry': "TEXT DEFAULT ''",
            'location': "TEXT DEFAULT ''",
            'notes': "TEXT DEFAULT ''",
        }
        for col, col_type in new_columns.items():
            if col not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE assets ADD COLUMN {col} {col_type}")
                except sqlite3.OperationalError:
                    pass
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


# Initialize the DB instance once
db = SQLiteDB("assets.db")
