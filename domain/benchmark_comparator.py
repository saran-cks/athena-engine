from typing import List, Tuple, Optional
from datetime import date
from domain.entities import CashFlow, Instrument, ComparisonResult, Transaction
from domain.investment_simulator import InvestmentSimulator
from domain.metrics_engine import MetricsEngine


class BenchmarkComparator:

    def __init__(self, simulator: InvestmentSimulator):
        self.simulator = simulator

    def compare(
        self,
        portfolio_id: str,
        actual_xirr: float,
        actual_value: float,
        total_invested: float,
        actual_cagr: float,
        actual_abs_return: float,
        actual_max_dd: float,
        actual_contributions: dict,
        actual_timeline: List[Tuple[date, float]],
        actual_unit_nav: List[Tuple[date, float]],
        aggregated_investment_cashflows: List[CashFlow],
        benchmark_instrument: Instrument,
        valuation_date: date,
    ) -> ComparisonResult:

        # 1. Rebuild transactions for simulator (positive amounts)
        benchmark_txs = [
            Transaction(
                date=cf.date,
                amount=abs(cf.amount),
                instrument_id=benchmark_instrument.instrument_id,
                portfolio_id=portfolio_id,
            )
            for cf in aggregated_investment_cashflows
            if cf.amount < 0
        ]

        # 2. Simulate
        sim_result = self.simulator.simulate(
            benchmark_txs,
            benchmark_instrument,
            valuation_date=valuation_date,
        )

        # 3. Metrics
        benchmark_xirr = MetricsEngine.calculate_xirr(sim_result.cashflows)
        alpha = MetricsEngine.calculate_alpha(actual_xirr, benchmark_xirr)

        benchmark_unit_nav = MetricsEngine.unitize_timeline(
            sim_result.portfolio_value_timeline,
            aggregated_investment_cashflows,
        )
        benchmark_cagr = MetricsEngine.calculate_annualized_return(benchmark_unit_nav)
        benchmark_abs = MetricsEngine.calculate_absolute_return(
            total_invested, sim_result.current_value
        )
        benchmark_dd = MetricsEngine.calculate_max_drawdown(benchmark_unit_nav)

        act_roll, ben_roll, roll_alpha, up_cap, down_cap = (
            MetricsEngine.calculate_rolling_and_capture_from_nav(
                actual_unit_nav,
                benchmark_unit_nav,
            )
        )

        return ComparisonResult(
            portfolio_id=portfolio_id,
            benchmark=benchmark_instrument,
            actual_xirr=actual_xirr,
            benchmark_xirr=benchmark_xirr,
            alpha=alpha,
            actual_value=actual_value,
            benchmark_value=sim_result.current_value,
            total_invested=total_invested,
            actual_cagr=actual_cagr,
            benchmark_cagr=benchmark_cagr,
            actual_abs_return=actual_abs_return,
            benchmark_abs_return=benchmark_abs,
            actual_max_dd=actual_max_dd,
            benchmark_max_dd=benchmark_dd,
            actual_1y_rolling=act_roll,
            benchmark_1y_rolling=ben_roll,          # may be None
            rolling_alpha=roll_alpha,               # may be None
            upside_capture=up_cap,                  # may be None
            downside_capture=down_cap,              # may be None
            actual_contributions=actual_contributions,
            actual_timeline=actual_timeline,
            benchmark_timeline=sim_result.portfolio_value_timeline,
        )
