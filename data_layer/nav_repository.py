import sqlite3
import os
from datetime import date
from typing import List, Tuple

class NavRepository:
    """
    Data access layer for writing NAV data into and creating the SQLite DB.
    """
    def __init__(self, db_path: str = "db/nav_cache.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS nav_data (
                    scheme_code TEXT,
                    date TEXT,
                    nav REAL,
                    PRIMARY KEY (scheme_code, date)
                )
            ''')
            # An inherent index is created on (scheme_code, date) by the PRIMARY KEY.

    def upsert_bulk(self, records: List[Tuple[str, date, float]]):
        """
        Insert or update a bulk list of records gracefully.
        records: List of tuples (scheme_code, date, nav)
        """
        # Convert dates to ISO strings for SQLite storage
        insert_data = [(r[0], r[1].isoformat(), r[2]) for r in records]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany('''
                INSERT INTO nav_data (scheme_code, date, nav)
                VALUES (?, ?, ?)
                ON CONFLICT(scheme_code, date) DO UPDATE SET
                    nav = excluded.nav
            ''', insert_data)

    def insert_mfapi_history(self, scheme_code: str, history_data: List[dict]):
        """
        Helper method to bulk insert json `data` from mfapi.in response directly.
        """
        records = []
        for item in history_data:
            try:
                # mfapi format: 'dd-mm-yyyy'
                d_str = item['date']
                val = float(item['nav'])
                parts = d_str.split('-')
                dt = date(int(parts[2]), int(parts[1]), int(parts[0]))
                records.append((scheme_code, dt, val))
            except (ValueError, KeyError, IndexError):
                continue
                
        self.upsert_bulk(records)
