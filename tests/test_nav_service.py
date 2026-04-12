from datetime import date
from typing import Optional
from domain.interfaces import INavStore
from domain.nav_service import NavService

class MockStore(INavStore):
    def get_nav(self, scheme_code: str, target_date: date) -> Optional[float]:
        return 50.0  # static mock
    def get_nav_entry(self, scheme_code: str, target_date: date):
        return (date(2023, 1, 1), 50.0)
    def get_latest_nav_date(self, scheme_code: str) -> Optional[date]:
        return date(2024, 1, 1)
    def get_nav_range(self, scheme_code: str, start_date: date, end_date: date):
        return [(date(2023, 1, 1), 50.0)]
    def get_first_nav(self, scheme_code: str):
        return (date(2023, 1, 1), 50.0)

def test_nav_service_lookup():
    service = NavService(MockStore())
    val = service.get_nav("123", date(2023, 1, 1))
    assert val == 50.0
