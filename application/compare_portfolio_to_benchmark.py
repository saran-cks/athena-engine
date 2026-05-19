from domain.entities import Portfolio, ComparisonResult, Instrument
from domain.investment_simulator import InvestmentSimulator
from domain.portfolio_aggregator import PortfolioAggregator
from domain.metrics_engine import MetricsEngine
from domain.benchmark_comparator import BenchmarkComparator
from data_layer.instrument_registry import InstrumentRegistry
from domain.entities import CashFlow


class ComparePortfolioToBenchmark:
    def __init__(
        self,
        registry: InstrumentRegistry,
        simulator: InvestmentSimulator,
        aggregator: PortfolioAggregator,
        comparator: BenchmarkComparator,
    ):
        self.registry = registry
        self.simulator = simulator
        self.aggregator = aggregator
        self.comparator = comparator

    def execute(self, portfolio: Portfolio, benchmark: Instrument) -> ComparisonResult:
        # Group transactions by target instrument
        txs_by_instrument = {}
        for tx in portfolio.transactions:
            txs_by_instrument.setdefault(tx.instrument_id, []).append(tx)

        if not txs_by_instrument:
            raise ValueError("Portfolio has no valid investment transactions.")

        latest_dates = []
        last_tx_date = max(tx.date for tx in portfolio.transactions)
        for inst_id in txs_by_instrument:
            inst = self.registry.get(inst_id)
            if not inst:
                raise ValueError(
                    f"Instrument {inst_id} must be registered to simulate it."
                )
            latest_nav_date = self.simulator.nav_service.get_latest_nav_date(
                inst.scheme_code
            )
            if latest_nav_date is None:
                raise ValueError(
                    f"No NAV data available for '{inst.name}'. Ensure data is synced."
                )
            if latest_nav_date < last_tx_date:
                raise ValueError(
                    f"Portfolio fund '{inst.name}' has NAV history only up to {latest_nav_date}, but the portfolio has transactions through {last_tx_date}."
                )
            latest_dates.append(latest_nav_date)

        benchmark_latest_nav = self.simulator.nav_service.get_latest_nav_date(
            benchmark.scheme_code
        )
        if benchmark_latest_nav is None:
            raise ValueError(
                f"No NAV data available for benchmark '{benchmark.name}'. Ensure data is synced."
            )
        latest_dates.append(benchmark_latest_nav)

        common_valuation_date = min(latest_dates)
        if common_valuation_date < last_tx_date:
            raise ValueError(
                f"Common valuation date {common_valuation_date} is before the last transaction date {last_tx_date}. Sync NAV history for all selected instruments."
            )

        actual_total_current_value = 0.0
        total_invested = 0.0

        import pandas as pd

        series_list = []
        fund_value_timelines = []
        fund_unit_timelines = []
        actual_contributions = {}
        exact_simulated_cashflows_raw = {}

        # 1. Simulate the actual portfolio's real historical trajectory
        for inst_id, txs in txs_by_instrument.items():
            inst = self.registry.get(inst_id)
            sim_result = self.simulator.simulate(
                txs, inst, valuation_date=common_valuation_date
            )
            actual_total_current_value += sim_result.current_value
            total_invested += sim_result.invested_amount
            actual_contributions[inst.name] = sim_result.current_value

            # Map perfectly executed asynchronous cashflows to prevent NAV vol-bleed on long weekends
            for cf in sim_result.cashflows:
                if cf.amount < 0:
                    exact_simulated_cashflows_raw[cf.date] = (
                        exact_simulated_cashflows_raw.get(cf.date, 0.0) + cf.amount
                    )

            if sim_result.portfolio_value_timeline:
                fund_value_timelines.append(sim_result.portfolio_value_timeline)
                fund_unit_timelines.append(
                    MetricsEngine.unitize_timeline(
                        sim_result.portfolio_value_timeline,
                        sim_result.cashflows,
                    )
                )
                dates = [d for d, v in sim_result.portfolio_value_timeline]
                values = [v for d, v in sim_result.portfolio_value_timeline]
                s = pd.Series(values, index=pd.to_datetime(dates), name=inst_id)
                series_list.append(s)

        if series_list:
            combined_df = pd.concat(series_list, axis=1)
            # FFill missing interior dates natively to prevent artificial summing drops when one fund updates late
            combined_df = combined_df.sort_index().ffill().fillna(0.0)
            combined_series = combined_df.sum(axis=1)
            actual_timeline = [(d.date(), v) for d, v in combined_series.items()]
        else:
            actual_timeline = []

        # 2. Extract merged precision executed cashflows
        exact_aligned_cashflows = [
            CashFlow(date=d, amount=amt)
            for d, amt in exact_simulated_cashflows_raw.items()
        ]
        exact_aligned_cashflows.sort(key=lambda cf: cf.date)

        # 3. Calculate portfolio's real composite XIRR
        xirr_cf = exact_aligned_cashflows.copy()
        terminal_date = common_valuation_date
        xirr_cf.append(CashFlow(date=terminal_date, amount=actual_total_current_value))
        actual_xirr = MetricsEngine.calculate_xirr(xirr_cf)

        actual_unit_nav = MetricsEngine.aggregate_portfolio_unit_nav(
            fund_value_timelines,
            fund_unit_timelines,
        )
        actual_cagr = MetricsEngine.calculate_annualized_return(actual_unit_nav)
        actual_abs_return = MetricsEngine.calculate_absolute_return(
            total_invested, actual_total_current_value
        )
        actual_max_dd = MetricsEngine.calculate_max_drawdown(actual_unit_nav)

        # 4. Compare vs Benchmark
        return self.comparator.compare(
            portfolio_id=portfolio.portfolio_id,
            actual_xirr=actual_xirr,
            actual_value=actual_total_current_value,
            total_invested=total_invested,
            actual_cagr=actual_cagr,
            actual_abs_return=actual_abs_return,
            actual_max_dd=actual_max_dd,
            actual_contributions=actual_contributions,
            actual_timeline=actual_timeline,
            actual_unit_nav=actual_unit_nav,
            aggregated_investment_cashflows=exact_aligned_cashflows,
            benchmark_instrument=benchmark,
            valuation_date=common_valuation_date,
        )
