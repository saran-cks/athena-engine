from datetime import date

from application.multi_benchmark_analysis import MultiBenchmarkAnalysis
from domain.entities import ComparisonResult, Instrument, Portfolio


class StubComparator:
    def execute(self, portfolio: Portfolio, benchmark: Instrument) -> ComparisonResult:
        if benchmark.instrument_id == "BAD":
            raise ValueError("Common valuation date 2016-11-25 is before the last transaction date 2026-04-06.")

        return ComparisonResult(
            portfolio_id=portfolio.portfolio_id,
            benchmark=benchmark,
            actual_xirr=0.10,
            benchmark_xirr=0.08,
            alpha=0.02,
            actual_value=110.0,
            benchmark_value=108.0,
            total_invested=100.0,
        )


def test_multi_benchmark_analysis_skips_invalid_benchmarks():
    use_case = MultiBenchmarkAnalysis(StubComparator())
    portfolio = Portfolio(portfolio_id="P1", owner="u", transactions=[])
    good = Instrument("GOOD", "Good Bench", "G", "index_fund")
    bad = Instrument("BAD", "Bad Bench", "B", "index_fund")

    results = use_case.execute(portfolio, [good, bad])

    assert len(results) == 1
    assert results[0].benchmark.name == "Good Bench"
    assert use_case.last_errors == [
        ("Bad Bench", "Common valuation date 2016-11-25 is before the last transaction date 2026-04-06.")
    ]
