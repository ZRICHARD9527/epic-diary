"""
SQLite Indexing Layer for EpicDiary v4.0
Purpose: Fast queries, full-text search, and relationship mapping
Philosophy: Complementary to Markdown persistence - not a replacement
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "diary", "epic_index.db")

class EpicDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db_exists()
        self._init_schema()

    def _ensure_db_exists(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _init_schema(self):
        """Initialize database schema if not exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_folder TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    weather TEXT,
                    real_text TEXT,
                    drama_text TEXT,
                    emoji TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date_folder, timestamp)
                )
            """)
            
            # Full-text search virtual table
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS entries_ft
                USING fts5(
                    real_text,
                    drama_text,
                    content='entries',
                    content_rowid='id'
                )
            """)
            
            # Memory relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_entry_id INTEGER NOT NULL,
                    to_entry_id INTEGER NOT NULL,
                    relationship_type TEXT DEFAULT 'related',
                    strength REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (from_entry_id) REFERENCES entries(id),
                    FOREIGN KEY (to_entry_id) REFERENCES entries(id),
                    UNIQUE(from_entry_id, to_entry_id)
                )
            """)
            
            # Tags/themes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#8b7355'
                )
            """)
            
            #Entry-tag junction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entry_tags (
                    entry_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    FOREIGN KEY (entry_id) REFERENCES entries(id),
                    FOREIGN KEY (tag_id) REFERENCES tags(id),
                    PRIMARY KEY (entry_id, tag_id)
                )
            """)
            
            conn.commit()

    def index_entry(self, date_folder: str, timestamp: str, weather: str, 
                   real_text: str, drama_text: str, emoji: str) -> Optional[int]:
        """Index a diary entry in SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO entries 
                    (date_folder, timestamp, weather, real_text, drama_text, emoji)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (date_folder, timestamp, weather, real_text, drama_text, emoji))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.error(f"Failed to index entry: {e}")
            return None

    def search_entries(self, query: str, limit: int = 20) -> List[Dict]:
        """Full-text search across entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT e.* FROM entries e
                    JOIN entries_ft fts ON e.id = fts.rowid
                    WHERE entries_ft MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """, (query, limit))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return []

    def get_related_entries(self, date_folder: str, timestamp: str, 
                           limit: int = 5) -> List[Dict]:
        """Find related entries based on relationships"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get entry ID
                cursor.execute("""
                    SELECT id FROM entries 
                    WHERE date_folder = ? AND timestamp = ?
                """, (date_folder, timestamp))
                result = cursor.fetchone()
                
                if not result:
                    return []
                
                entry_id = result['id']
                
                # Get related entries
                cursor.execute("""
                    SELECT e.* FROM entries e
                    JOIN relationships r ON e.id = r.to_entry_id
                    WHERE r.from_entry_id = ?
                    ORDER BY r.strength DESC
                    LIMIT ?
                """, (entry_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Failed to get related entries: {e}")
            return []

    def suggest_relationships(self, date_folder: str, timestamp: str) -> List[Dict]:
        """AI-agnostic relationship suggestions based on content similarity"""
        # This is a placeholder for future ML-based relationship detection
        # Currently returns empty list
        return []

    def get_entry_by_id(self, entry_id: int) -> Optional[Dict]:
        """Get entry by database ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logging.error(f"Failed to get entry by ID: {e}")
            return None

    def get_all_entries_by_date(self, date_folder: str) -> List[Dict]:
        """Get all entries for a specific date"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM entries 
                    WHERE date_folder = ?
                    ORDER BY timestamp DESC
                """, (date_folder,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Failed to get entries by date: {e}")
            return []

    def delete_entry(self, date_folder: str, timestamp: str):
        """Remove entry from index"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM entries 
                    WHERE date_folder = ? AND timestamp = ?
                """, (date_folder, timestamp))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to delete entry from index: {e}")

# Global database instance
_db_instance = None

def get_database() -> EpicDatabase:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = EpicDatabase()
    return _db_instance
