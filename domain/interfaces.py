from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List, Tuple

class INavStore(ABC):
    """
    Interface for querying Net Asset Value (NAV) data.
    Implementations must enforce nearest-previous-date fallback for non-trading days.
    """
    
    @abstractmethod
    def get_nav(self, scheme_code: str, target_date: date) -> Optional[float]:
        """
        Retrieves the NAV for a given scheme on a specific date.
        If the exact date is not a trading day or NAV is missing, it should return 
        the NAV of the nearest previous trading day.
        
        Returns None if no NAV data exists at all for or before the target_date.
        """
        pass

    @abstractmethod
    def get_nav_entry(self, scheme_code: str, target_date: date) -> Optional[Tuple[date, float]]:
        """
        Retrieves the nearest on-or-before NAV record as (nav_date, nav_value).
        Returns None if no NAV data exists at all for or before the target_date.
        """
        pass
        
    @abstractmethod
    def get_latest_nav_date(self, scheme_code: str) -> Optional[date]:
        """
        Retrieves the most recent date for which NAV data is available for the scheme.
        """
        pass
        
    @abstractmethod
    def get_nav_range(self, scheme_code: str, start_date: date, end_date: date) -> List[Tuple[date, float]]:
        """
        Retrieves a dense chronological list of all (date, nav) readings between the start and end dates.
        """
        pass

    @abstractmethod
    def get_first_nav(self, scheme_code: str) -> Optional[Tuple[date, float]]:
        """
        Retrieves the earliest available NAV record for the given scheme, useful for inception fallback handling.
        """
        pass
