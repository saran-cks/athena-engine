from datetime import date
from typing import Optional
from domain.entities import Transaction, Instrument
from domain.investment_simulator import InvestmentSimulator
from domain.nav_service import NavService
from domain.interfaces import INavStore


class StaticIncrementStore(INavStore):
    def get_nav(self, scheme_code: str, target_date: date) -> Optional[float]:
        if target_date == date(2023, 1, 1):
            return 10.0
        if target_date == date(2023, 2, 1):
            return 20.0
        if target_date == date(2024, 1, 1):
            return 25.0
        return 10.0

    def get_nav_entry(self, scheme_code: str, target_date: date):
        if target_date >= date(2024, 1, 1):
            return (date(2024, 1, 1), 25.0)
        if target_date >= date(2023, 2, 1):
            return (date(2023, 2, 1), 20.0)
        return (date(2023, 1, 1), 10.0)

    def get_latest_nav_date(self, scheme_code: str) -> Optional[date]:
        return date(2024, 1, 1)

    def get_nav_range(self, scheme_code: str, start_date: date, end_date: date):
        points = [
            (date(2023, 1, 1), 10.0),
            (date(2023, 2, 1), 20.0),
            (date(2024, 1, 1), 25.0),
        ]
        return [(dt, nav) for dt, nav in points if start_date <= dt <= end_date]

    def get_first_nav(self, scheme_code: str):
        return (date(2023, 1, 1), 10.0)


def test_simulation_accurate_unit_calculation():
    nav_s = NavService(StaticIncrementStore())
    sim = InvestmentSimulator(nav_s)

    inst = Instrument("TEST_ID", "Test Fund", "SCH", "index_fund")
    txs = [
        Transaction(date(2023, 1, 1), 1000.0, "TEST_ID", "PORTFOLIO"),  # buys 100 units
        Transaction(date(2023, 2, 1), 1000.0, "TEST_ID", "PORTFOLIO"),  # buys 50 units
    ]

    # Total units = 150
    # Final date 2024-01-01 nav = 25.0. Value = 150 * 25 = 3750
    res = sim.simulate(txs, inst)

    assert abs(res.total_units - 150.0) < 0.001
    assert abs(res.invested_amount - 2000.0) < 0.001
    assert abs(res.current_value - 3750.0) < 0.001
    # Check expected final cashflow counts plus terminal
    assert len(res.cashflows) == 3
    assert res.cashflows[-1].amount == 3750.0
