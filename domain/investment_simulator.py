from datetime import date
from typing import List
from domain.entities import Transaction, Instrument, SimulationResult, CashFlow
from domain.nav_service import NavService


class InvestmentSimulator:
    """
    Core engine to simulate playing back a series of historical transactions
    against a target instrument (e.g. mutual fund or an index proxy).
    """

    def __init__(self, nav_service: NavService):
        self.nav_service = nav_service

    @staticmethod
    def _resolve_nav_or_raise(
        nav_service: NavService,
        scheme_code: str,
        instrument_name: str,
        target_date: date,
        max_staleness_days: int = 7,
    ) -> float:
        entry = nav_service.get_nav_entry(scheme_code, target_date)
        if entry is None:
            first_nav_data = nav_service.get_first_nav(scheme_code)
            if first_nav_data is not None and target_date < first_nav_data[0]:
                return first_nav_data[1]
            raise RuntimeError(
                f"Failed to find NAV for '{instrument_name}' on or before {target_date}."
            )

        nav_date, nav_value = entry
        staleness = (target_date - nav_date).days
        if staleness > max_staleness_days:
            raise RuntimeError(
                f"Stale NAV for '{instrument_name}': latest usable NAV on or before {target_date} is {nav_date} ({staleness} days old)."
            )
        return nav_value

    def simulate(
        self,
        transactions: List[Transaction],
        target_instrument: Instrument,
        valuation_date: date | None = None,
    ) -> SimulationResult:
        if not transactions:
            raise ValueError("Cannot simulate an empty list of transactions.")

        # Ensure chronological order for simulation
        sorted_txs = sorted(transactions, key=lambda tx: tx.date)

        # Determine the final valuation date. Look up the latest available NAV date.
        latest_nav_date = self.nav_service.get_latest_nav_date(
            target_instrument.scheme_code
        )
        if not latest_nav_date:
            raise ValueError(
                f"No NAV data available for '{target_instrument.name}' ({target_instrument.scheme_code}). Ensure data is synced."
            )

        last_tx_date = sorted_txs[-1].date
        if valuation_date is not None:
            if valuation_date < last_tx_date:
                raise ValueError(
                    f"Valuation date {valuation_date} is before the last transaction date {last_tx_date}."
                )
            end_date = min(latest_nav_date, valuation_date)
        else:
            end_date = latest_nav_date

        if end_date < last_tx_date:
            raise ValueError(
                f"Latest NAV date {latest_nav_date} for '{target_instrument.name}' is before the last transaction date {last_tx_date}."
            )

        total_units = 0.0
        invested_amount = 0.0
        cashflows: List[CashFlow] = []

        # We record the ending unit balance on every transaction day to build the daily timeline later
        balances = []

        for tx in sorted_txs:
            if tx.amount <= 0:
                continue

            nav = self._resolve_nav_or_raise(
                self.nav_service,
                target_instrument.scheme_code,
                target_instrument.name,
                tx.date,
            )

            units_bought = tx.amount / nav
            total_units += units_bought
            invested_amount += tx.amount

            cashflows.append(CashFlow(date=tx.date, amount=-tx.amount))
            balances.append((tx.date, total_units))

        # Fetch the complete actual NAV history for dense plotting / drawdown calculations
        nav_history = self.nav_service.get_nav_range(
            target_instrument.scheme_code, sorted_txs[0].date, end_date
        )

        timeline_nav = []
        portfolio_value_timeline = []

        current_units = 0.0
        bal_idx = 0

        for dt, nav in nav_history:
            # Advance bal_idx to incorporate any transactions that happened on or before this day
            while bal_idx < len(balances) and balances[bal_idx][0] <= dt:
                current_units = balances[bal_idx][1]
                bal_idx += 1

            if current_units > 0:
                timeline_nav.append((dt, nav))
                portfolio_value_timeline.append((dt, current_units * nav))

        # Final valuation point
        final_nav = self._resolve_nav_or_raise(
            self.nav_service,
            target_instrument.scheme_code,
            target_instrument.name,
            end_date,
        )

        current_value = total_units * final_nav

        simulated_cashflows = cashflows.copy()
        simulated_cashflows.append(CashFlow(date=end_date, amount=current_value))

        # Fallback if history loop was completely empty for some reason
        if not timeline_nav or timeline_nav[-1][0] != end_date:
            timeline_nav.append((end_date, final_nav))
            portfolio_value_timeline.append((end_date, current_value))

        return SimulationResult(
            instrument=target_instrument,
            total_units=total_units,
            invested_amount=invested_amount,
            current_value=current_value,
            cashflows=simulated_cashflows,
            timeline_nav=timeline_nav,
            portfolio_value_timeline=portfolio_value_timeline,
        )
