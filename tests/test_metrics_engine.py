from datetime import date
from domain.entities import CashFlow
from domain.metrics_engine import MetricsEngine

def test_xirr_calculation():
    # Example sequence mimicking typical SIP behavior
    cashflows = [
        CashFlow(date(2023, 1, 1), -10000),  # invest 10k
        CashFlow(date(2023, 2, 1), -10000),  # invest 10k
        CashFlow(date(2023, 3, 1), -10000),  # invest 10k
        CashFlow(date(2024, 3, 1), 35000),   # final value is positive
    ]
    val = MetricsEngine.calculate_xirr(cashflows)
    
    # Just asserting it returns a positive return float rather than erroring
    assert val > 0.05
    
def test_max_drawdown():
    timeline = [
        (date(2023, 1, 1), 100.0),
        (date(2023, 1, 2), 110.0), # peak
        (date(2023, 1, 3), 88.0),  # 20% drawdown from 110
        (date(2023, 1, 4), 95.0),
    ]
    dd = MetricsEngine.calculate_max_drawdown(timeline)
    assert abs(dd - 0.20) < 0.001

def test_cagr():
    cagr = MetricsEngine.calculate_cagr(100.0, 150.0, 5.0)
    assert abs(cagr - 0.08447) < 0.001


def test_unitized_drawdown_ignores_contributions():
    timeline = [
        (date(2023, 1, 1), 100.0),
        (date(2023, 1, 2), 110.0),
        (date(2023, 1, 3), 210.0),  # value jump includes a new 100 contribution
        (date(2023, 1, 4), 205.0),
    ]
    cashflows = [CashFlow(date(2023, 1, 3), -100.0)]

    unitized = MetricsEngine.unitize_timeline(timeline, cashflows, tolerance_days=0)
    dd = MetricsEngine.calculate_max_drawdown(unitized)

    # After stripping the contribution, the portfolio is flat on day 3 and then falls from 210 to 205.
    assert abs(dd - (5.0 / 210.0)) < 0.001


def test_capture_ratios_use_linked_returns():
    port_nav = [
        (date(2023, 1, 31), 100.0),
        (date(2023, 2, 28), 120.0),  # +20%
        (date(2023, 3, 31), 108.0),  # -10%
        (date(2023, 4, 30), 118.8),  # +10%
    ]
    bench_nav = [
        (date(2023, 1, 31), 100.0),
        (date(2023, 2, 28), 110.0),  # +10%
        (date(2023, 3, 31), 104.5),  # -5%
        (date(2023, 4, 30), 109.725),  # +5%
    ]

    up_capture, down_capture = MetricsEngine._calc_capture_ratios(port_nav, bench_nav)

    # Upside: linked portfolio return = 1.2 * 1.1 - 1 = 32%
    # Benchmark linked return = 1.1 * 1.05 - 1 = 15.5%
    assert abs(up_capture - (0.32 / 0.155)) < 0.001
    assert abs(down_capture - (0.10 / 0.05)) < 0.001


def test_annualized_return_uses_unitized_series():
    unitized = [
        (date(2023, 1, 1), 100.0),
        (date(2024, 1, 1), 121.0),
    ]

    annualized = MetricsEngine.calculate_annualized_return(unitized)
    assert abs(annualized - 0.21) < 0.002


def test_aggregate_portfolio_unit_nav_links_fund_returns():
    fund_a_values = [
        (date(2024, 1, 1), 100.0),
        (date(2024, 1, 2), 110.0),
    ]
    fund_a_unit = [
        (date(2024, 1, 1), 100.0),
        (date(2024, 1, 2), 110.0),
    ]

    fund_b_values = [
        (date(2024, 1, 1), 100.0),
        (date(2024, 1, 2), 100.0),
    ]
    fund_b_unit = [
        (date(2024, 1, 1), 100.0),
        (date(2024, 1, 2), 100.0),
    ]

    portfolio_unit = MetricsEngine.aggregate_portfolio_unit_nav(
        [fund_a_values, fund_b_values],
        [fund_a_unit, fund_b_unit],
    )

    assert portfolio_unit[0] == (date(2024, 1, 1), 100.0)
    # Prior-day weights are 50/50, so day-2 portfolio return should be +5%.
    assert abs(portfolio_unit[-1][1] - 105.0) < 0.001


def test_unitize_timeline_aggregates_same_day_cashflows():
    timeline = [
        (date(2025, 8, 4), 17000.0),
        (date(2025, 8, 5), 17051.0),
        (date(2025, 9, 9), 20624.0),
    ]
    cashflows = [
        CashFlow(date(2025, 8, 4), -15000.0),
        CashFlow(date(2025, 8, 4), -2000.0),
        CashFlow(date(2025, 9, 9), -2000.0),
    ]

    unitized = MetricsEngine.unitize_timeline(timeline, cashflows, tolerance_days=3)

    assert abs(unitized[0][1] - 100.0) < 0.001
    # The second same-day cashflow must not spill into the next trading day.
    assert unitized[1][1] > 100.0
    assert abs(unitized[2][1] - 109.55) < 0.5
