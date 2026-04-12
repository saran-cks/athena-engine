from datetime import date
from typing import Optional, List, Tuple

from application.compare_portfolio_to_benchmark import ComparePortfolioToBenchmark
from domain.benchmark_comparator import BenchmarkComparator
from domain.entities import Instrument, Portfolio, Transaction
from domain.investment_simulator import InvestmentSimulator
from domain.nav_service import NavService
from domain.portfolio_aggregator import PortfolioAggregator
from domain.interfaces import INavStore


class StaticRegistry:
    def __init__(self, instruments):
        self._instruments = {inst.instrument_id: inst for inst in instruments}

    def get(self, instrument_id: str):
        return self._instruments.get(instrument_id)


class FixedNavStore(INavStore):
    def __init__(self):
        self.data = {
            "ACTUAL": [
                (date(2023, 1, 1), 10.0),
                (date(2023, 6, 1), 11.0),
                (date(2023, 9, 1), 11.5),
                (date(2024, 1, 1), 12.0),
            ],
            "BENCH": [
                (date(2023, 1, 1), 10.0),
                (date(2023, 6, 1), 12.0),
                (date(2023, 9, 1), 13.0),
            ],
        }

    def get_nav(self, scheme_code: str, target_date: date) -> Optional[float]:
        eligible = [nav for dt, nav in self.data[scheme_code] if dt <= target_date]
        return eligible[-1] if eligible else None

    def get_nav_entry(self, scheme_code: str, target_date: date) -> Optional[Tuple[date, float]]:
        eligible = [(dt, nav) for dt, nav in self.data[scheme_code] if dt <= target_date]
        return eligible[-1] if eligible else None

    def get_latest_nav_date(self, scheme_code: str) -> Optional[date]:
        return self.data[scheme_code][-1][0]

    def get_nav_range(self, scheme_code: str, start_date: date, end_date: date) -> List[Tuple[date, float]]:
        return [
            (dt, nav)
            for dt, nav in self.data[scheme_code]
            if start_date <= dt <= end_date
        ]

    def get_first_nav(self, scheme_code: str) -> Optional[Tuple[date, float]]:
        return self.data[scheme_code][0]


def test_analysis_uses_common_valuation_date_for_actual_and_benchmark():
    actual_inst = Instrument("ACTUAL_ID", "Actual Fund", "ACTUAL", "mutual_fund")
    bench_inst = Instrument("BENCH_ID", "Benchmark Fund", "BENCH", "index_fund")

    portfolio = Portfolio(
        portfolio_id="P1",
        owner="user",
        transactions=[
            Transaction(date(2023, 1, 1), 1000.0, actual_inst.instrument_id, "P1"),
        ],
    )

    registry = StaticRegistry([actual_inst, bench_inst])
    nav_service = NavService(FixedNavStore())
    simulator = InvestmentSimulator(nav_service)
    comparator = BenchmarkComparator(simulator)
    use_case = ComparePortfolioToBenchmark(
        registry,
        simulator,
        PortfolioAggregator(),
        comparator,
    )

    result = use_case.execute(portfolio, bench_inst)

    assert result.actual_timeline[-1][0] == date(2023, 9, 1)
    assert result.benchmark_timeline[-1][0] == date(2023, 9, 1)
