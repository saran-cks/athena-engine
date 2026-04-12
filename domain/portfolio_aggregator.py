from typing import List, Dict, Tuple
from datetime import date
from domain.entities import Portfolio, CashFlow, Transaction


class PortfolioAggregator:
    """
    Merges transactions from multiple funds into:
      1. A unified cashflow stream (for XIRR) — same as before
      2. Fund-level transaction groups (for dense timeline building)
    """

    def aggregate(self, portfolio: Portfolio) -> List[CashFlow]:
        """
        Unified investment cashflows (outflows, negative) sorted chronologically.
        Used for XIRR and as input to BenchmarkComparator.
        """
        daily_investments: Dict[date, float] = {}

        for tx in portfolio.transactions:
            if tx.amount <= 0:
                continue
            daily_investments[tx.date] = (
                daily_investments.get(tx.date, 0.0) + tx.amount
            )

        cashflows = [
            CashFlow(date=d, amount=-amt)
            for d, amt in daily_investments.items()
        ]
        cashflows.sort(key=lambda cf: cf.date)
        return cashflows

    def group_by_instrument(
        self, portfolio: Portfolio
    ) -> Dict[str, List[Transaction]]:
        """
        Returns transactions grouped by instrument_id, each list sorted by date.
        Used by the use case layer to simulate each fund separately
        and then stitch together a dense daily portfolio value timeline.
        """
        groups: Dict[str, List[Transaction]] = {}
        for tx in portfolio.transactions:
            if tx.amount <= 0:
                continue
            groups.setdefault(tx.instrument_id, []).append(tx)

        for instrument_id in groups:
            groups[instrument_id].sort(key=lambda tx: tx.date)

        return groups