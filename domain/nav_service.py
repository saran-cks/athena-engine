from domain.interfaces import INavStore
from datetime import date
from typing import Optional, List, Tuple

class NavService:
    """
    Domain service for NAV lookups. 
    It delegates to an injected INavStore to maintain strict 
    separation between Domain and Data logic.
    """
    def __init__(self, nav_store: INavStore):
        self.nav_store = nav_store
        
    def get_nav(self, scheme_code: str, target_date: date) -> Optional[float]:
        """
        Get the NAV for a specific scheme code and date.
        Provides fallback logic via the store implementation.
        """
        return self.nav_store.get_nav(scheme_code, target_date)

    def get_nav_entry(self, scheme_code: str, target_date: date) -> Optional[Tuple[date, float]]:
        """
        Get the nearest on-or-before NAV record for a specific scheme code and date.
        """
        return self.nav_store.get_nav_entry(scheme_code, target_date)
        
    def get_latest_nav_date(self, scheme_code: str) -> Optional[date]:
        """
        Get the most recent date we have NAV data for a given scheme.
        """
        return self.nav_store.get_latest_nav_date(scheme_code)
        
    def get_nav_range(self, scheme_code: str, start_date: date, end_date: date) -> List[Tuple[date, float]]:
        """
        Get bounded array of chronological NAV values.
        """
        return self.nav_store.get_nav_range(scheme_code, start_date, end_date)

    def get_first_nav(self, scheme_code: str) -> Optional[Tuple[date, float]]:
        """
        Get earliest bounded available NAV value.
        """
        return self.nav_store.get_first_nav(scheme_code)
