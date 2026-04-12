from datetime import date
from typing import Optional

import pytest

from application.compare_portfolio_to_benchmark import ComparePortfolioToBenchmark
from domain.benchmark_comparator import BenchmarkComparator
from domain.entities import Instrument, Portfolio, Transaction
from domain.investment_simulator import InvestmentSimulator
from domain.interfaces import INavStore
from domain.nav_service import NavService
from domain.portfolio_aggregator import PortfolioAggregator


class StaticRegistry:
    def __init__(self, instruments):
        self._instruments = {inst.instrument_id: inst for inst in instruments}

    def get(self, instrument_id: str):
        return self._instruments.get(instrument_id)


class StaleActualStore(INavStore):
    def get_nav(self, scheme_code: str, target_date: date) -> Optional[float]:
        entry = self.get_nav_entry(scheme_code, target_date)
        return entry[1] if entry else None

    def get_nav_entry(self, scheme_code: str, target_date: date):
        if scheme_code == "STALE":
            return (date(2016, 11, 25), 100.0)
        if scheme_code == "BENCH":
            return (date(2026, 4, 10), 100.0)
        return None

    def get_latest_nav_date(self, scheme_code: str) -> Optional[date]:
        if scheme_code == "STALE":
            return date(2016, 11, 25)
        if scheme_code == "BENCH":
            return date(2026, 4, 10)
        return None

    def get_nav_range(self, scheme_code: str, start_date: date, end_date: date):
        return []

    def get_first_nav(self, scheme_code: str):
        if scheme_code == "STALE":
            return (date(2013, 1, 1), 90.0)
        if scheme_code == "BENCH":
            return (date(2013, 1, 1), 90.0)
        return None


def test_compare_portfolio_reports_stale_actual_fund_explicitly():
    actual_inst = Instrument("ACTUAL_ID", "Stale Fund", "STALE", "mutual_fund")
    bench_inst = Instrument("BENCH_ID", "Benchmark Fund", "BENCH", "index_fund")
    portfolio = Portfolio(
        portfolio_id="P1",
        owner="user",
        transactions=[Transaction(date(2026, 4, 6), 1000.0, actual_inst.instrument_id, "P1")],
    )

    registry = StaticRegistry([actual_inst, bench_inst])
    nav_service = NavService(StaleActualStore())
    simulator = InvestmentSimulator(nav_service)
    comparator = BenchmarkComparator(simulator)
    use_case = ComparePortfolioToBenchmark(
        registry,
        simulator,
        PortfolioAggregator(),
        comparator,
    )

    with pytest.raises(ValueError, match="Portfolio fund 'Stale Fund' has NAV history only up to 2016-11-25"):
        use_case.execute(portfolio, bench_inst)
