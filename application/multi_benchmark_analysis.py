from typing import List
from domain.entities import Portfolio, ComparisonResult, Instrument
from application.compare_portfolio_to_benchmark import ComparePortfolioToBenchmark

class MultiBenchmarkAnalysis:
    def __init__(self, portfolio_comparator: ComparePortfolioToBenchmark):
        self.portfolio_comparator = portfolio_comparator
        self.last_errors: List[tuple[str, str]] = []
        
    def execute(self, portfolio: Portfolio, benchmarks: List[Instrument]) -> List[ComparisonResult]:
        """
        Evaluates a single portfolio against multiple separate benchmarks concurrently.
        Outputs a comparison result for each benchmark to allow table rendering.
        """
        results = []
        self.last_errors = []
        for b in benchmarks:
            try:
                res = self.portfolio_comparator.execute(portfolio, b)
                results.append(res)
            except Exception as exc:
                self.last_errors.append((b.name, str(exc)))
            
        return results
