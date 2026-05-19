from typing import List
from domain.entities import Portfolio, ComparisonResult, Instrument
from application.compare_portfolio_to_benchmark import ComparePortfolioToBenchmark


class CompareMultiplePortfolios:
    def __init__(self, portfolio_comparator: ComparePortfolioToBenchmark):
        self.portfolio_comparator = portfolio_comparator

    def execute(
        self, portfolios: List[Portfolio], benchmark: Instrument
    ) -> List[ComparisonResult]:
        """
        A macro use-case that evaluates several distinct portfolios against a single benchmark.
        E.g. "My Portfolio" vs "Friend's Portfolio" compared to Nifty 50.
        """
        results = []
        for p in portfolios:
            res = self.portfolio_comparator.execute(p, benchmark)
            results.append(res)

        return results
