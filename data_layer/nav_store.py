import sqlite3
from datetime import date
from typing import Optional, List, Tuple
from domain.interfaces import INavStore

class NavStore(INavStore):
    """
    Implements INavStore. Serves read queries directly from SQLite
    with built-in fallback for non-trading days.
    """
    def __init__(self, db_path: str = "db/nav_cache.db"):
        self.db_path = db_path
        
    def get_nav(self, scheme_code: str, target_date: date) -> Optional[float]:
        """
        Nearest-previous-date fallback: Returns exact date, or if not found, 
        the closest older date.
        """
        entry = self.get_nav_entry(scheme_code, target_date)
        return entry[1] if entry else None

    def get_nav_entry(self, scheme_code: str, target_date: date) -> Optional[Tuple[date, float]]:
        """
        Returns the nearest NAV record on or before target_date.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT date, nav FROM nav_data
                WHERE scheme_code = ? AND date <= ?
                ORDER BY date DESC
                LIMIT 1
            ''', (scheme_code, target_date.isoformat()))
            row = cursor.fetchone()
            if row:
                return date.fromisoformat(row[0]), row[1]
            return None
            
    def get_latest_nav_date(self, scheme_code: str) -> Optional[date]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT date FROM nav_data
                WHERE scheme_code = ?
                ORDER BY date DESC
                LIMIT 1
            ''', (scheme_code,))
            row = cursor.fetchone()
            if row:
                return date.fromisoformat(row[0])
            return None
            
    def get_nav_range(self, scheme_code: str, start_date: date, end_date: date) -> List[Tuple[date, float]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT date, nav FROM nav_data
                WHERE scheme_code = ? AND date >= ? AND date <= ?
                ORDER BY date ASC
            ''', (scheme_code, start_date.isoformat(), end_date.isoformat()))
            results = []
            for row in cursor.fetchall():
                results.append((date.fromisoformat(row[0]), row[1]))
            return results

    def get_first_nav(self, scheme_code: str) -> Optional[Tuple[date, float]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT date, nav FROM nav_data
                WHERE scheme_code = ?
                ORDER BY date ASC
                LIMIT 1
            ''', (scheme_code,))
            row = cursor.fetchone()
            if row:
                return date.fromisoformat(row[0]), row[1]
            return None
