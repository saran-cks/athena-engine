import argparse
import os
import pickle
import sys
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from application.compare_portfolio_to_benchmark import ComparePortfolioToBenchmark
from application.multi_benchmark_analysis import MultiBenchmarkAnalysis
from data_layer.instrument_registry import InstrumentRegistry
from data_layer.nav_store import NavStore
from domain.benchmark_comparator import BenchmarkComparator
from domain.entities import Portfolio, Transaction
from domain.investment_simulator import InvestmentSimulator
from domain.metrics_engine import MetricsEngine
from domain.nav_service import NavService
from domain.portfolio_aggregator import PortfolioAggregator


def build_services():
    registry = InstrumentRegistry()
    store = NavStore(os.path.join(ROOT, "db", "nav_cache.db"))
    nav_service = NavService(store)
    simulator = InvestmentSimulator(nav_service)
    aggregator = PortfolioAggregator()
    comparator = BenchmarkComparator(simulator)
    compare_use_case = ComparePortfolioToBenchmark(
        registry,
        simulator,
        aggregator,
        comparator,
    )
    multi_use_case = MultiBenchmarkAnalysis(compare_use_case)
    return registry, nav_service, simulator, compare_use_case, multi_use_case


def load_cached_portfolios():
    cache_path = os.path.join(ROOT, "db", "portfolio_cache.pkl")
    with open(cache_path, "rb") as f:
        return pickle.load(f)


def group_transactions(portfolio):
    groups = defaultdict(list)
    for tx in portfolio.transactions:
        groups[tx.instrument_id].append(tx)
    for txs in groups.values():
        txs.sort(key=lambda tx: tx.date)
    return groups


def common_actual_valuation_date(nav_service, registry, portfolio):
    dates = []
    for inst_id in group_transactions(portfolio):
        inst = registry.get(inst_id)
        dates.append(nav_service.get_latest_nav_date(inst.scheme_code))
    return min(dates)


def compute_portfolio_unit_nav(portfolio, registry, nav_service, simulator):
    groups = group_transactions(portfolio)
    valuation_date = common_actual_valuation_date(nav_service, registry, portfolio)
    fund_values = []
    fund_units = []
    for inst_id, txs in groups.items():
        inst = registry.get(inst_id)
        sim_result = simulator.simulate(txs, inst, valuation_date=valuation_date)
        fund_values.append(sim_result.portfolio_value_timeline)
        fund_units.append(
            MetricsEngine.unitize_timeline(
                sim_result.portfolio_value_timeline,
                sim_result.cashflows,
            )
        )
    return MetricsEngine.aggregate_portfolio_unit_nav(
        fund_values, fund_units
    ), valuation_date


def pct(value):
    if value is None:
        return "None"
    return f"{value * 100:.2f}%"


def scenario_1_same_day_boundary(
    ports, registry, nav_service, simulator, compare_use_case
):
    months = [
        date(2024, 4, 5),
        date(2024, 5, 6),
        date(2024, 6, 6),
        date(2024, 7, 8),
        date(2024, 8, 6),
        date(2024, 9, 6),
        date(2024, 10, 7),
        date(2024, 11, 6),
        date(2024, 12, 6),
        date(2025, 1, 6),
        date(2025, 2, 6),
        date(2025, 3, 6),
        date(2025, 4, 7),
        date(2025, 5, 6),
        date(2025, 6, 6),
        date(2025, 7, 7),
        date(2025, 8, 6),
        date(2025, 9, 8),
        date(2025, 10, 6),
        date(2025, 11, 6),
        date(2025, 12, 8),
        date(2026, 1, 6),
        date(2026, 2, 6),
        date(2026, 3, 6),
        date(2026, 4, 6),
    ]
    txs = [
        Transaction(months[0], 15000.0, "SBI_GOLD", "stress_same_day_sbi_gold"),
        Transaction(months[0], 2000.0, "SBI_GOLD", "stress_same_day_sbi_gold"),
    ]
    for tx_date in months[1:]:
        txs.append(Transaction(tx_date, 2000.0, "SBI_GOLD", "stress_same_day_sbi_gold"))

    isolated = Portfolio("stress_same_day_sbi_gold", "stress", txs)
    benchmark = registry.get("INDEX_NIFTY_50")
    result = compare_use_case.execute(isolated, benchmark)

    verdict = (
        result.actual_cagr > 0
        and result.actual_1y_rolling is not None
        and result.actual_1y_rolling > 0
        and result.actual_max_dd >= 0
        and result.actual_max_dd < 0.6
    )

    return {
        "portfolio": isolated.portfolio_id,
        "fund": registry.get("SBI_GOLD").name,
        "actual_xirr": result.actual_xirr,
        "twrr": result.actual_cagr,
        "rolling_1y": result.actual_1y_rolling,
        "max_dd": result.actual_max_dd,
        "verdict": verdict,
        "reason": "PASS" if verdict else "FAIL",
    }


def build_mixed_old_new_portfolio(portfolio):
    tx_dates = sorted(
        {tx.date for tx in portfolio.transactions if tx.instrument_id == "HDFC_DEFENCE"}
    )
    txs = []
    for idx, tx_date in enumerate(tx_dates, start=1):
        txs.append(Transaction(tx_date, 3000.0, "PPFAS_FLEXI", "stress_old_new"))
        txs.append(Transaction(tx_date, 3000.0, "INDEX_QUALITY", "stress_old_new"))
    return Portfolio("stress_old_new", "stress", txs)


def scenario_2_old_new_mix(
    ports, registry, nav_service, simulator, compare_use_case, multi_use_case
):
    base = ports["pf_prime"]
    mixed = build_mixed_old_new_portfolio(base)
    unit_nav, valuation_date = compute_portfolio_unit_nav(
        mixed, registry, nav_service, simulator
    )
    quality = registry.get("INDEX_QUALITY")
    quality_inception = nav_service.get_first_nav(quality.scheme_code)[0]

    returns = []
    for i in range(1, len(unit_nav)):
        prev_dt, prev_val = unit_nav[i - 1]
        dt, val = unit_nav[i]
        if prev_val > 0:
            returns.append((dt, val / prev_val - 1.0))

    window = [
        (dt, ret) for dt, ret in returns if abs((dt - quality_inception).days) <= 10
    ]
    max_abs_window = max((abs(ret) for _, ret in window), default=0.0)

    benchmark = registry.get("INDEX_NIFTY_50")
    single = compare_use_case.execute(mixed, benchmark)
    multi_results = multi_use_case.execute(mixed, registry.get_benchmarks())

    verdict = (
        max_abs_window < 0.15
        and len(multi_results) > 0
        and not multi_use_case.last_errors
    )

    return {
        "portfolio": mixed.portfolio_id,
        "valuation_date": valuation_date,
        "quality_inception": quality_inception,
        "window_returns": window,
        "max_abs_window_return": max_abs_window,
        "single_twrr": single.actual_cagr,
        "single_roll": single.actual_1y_rolling,
        "single_dd": single.actual_max_dd,
        "multi_count": len(multi_results),
        "multi_errors": list(multi_use_case.last_errors),
        "verdict": verdict,
        "reason": "PASS" if verdict else "CHECK",
    }


def scenario_3_outperforming_benchmarks(ports, registry, compare_use_case):
    portfolio = ports["pf_prime"]
    targets = ["INDEX_NASDAQ_100_BENCH", "INDEX_SP_500"]
    rows = []
    for inst_id in targets:
        bench = registry.get(inst_id)
        result = compare_use_case.execute(portfolio, bench)
        rows.append(
            {
                "benchmark": bench.name,
                "alpha": result.alpha,
                "bench_xirr": result.benchmark_xirr,
                "rolling_alpha": result.rolling_alpha,
                "upside_capture": result.upside_capture,
                "downside_capture": result.downside_capture,
            }
        )
    return rows


def print_scenario_1(out):
    print("SCENARIO 1: Lumpsum + same-day SIP boundary stress")
    print(f"Fund: {out['fund']}")
    print(f"Actual XIRR: {pct(out['actual_xirr'])}")
    print(f"TWRR: {pct(out['twrr'])}")
    print(f"1Y Rolling Avg: {pct(out['rolling_1y'])}")
    print(f"Max Drawdown: {pct(out['max_dd'])}")
    print(f"Verdict: {out['reason']}")
    print()


def print_scenario_2(out):
    print("SCENARIO 2: New fund vs old fund in same portfolio")
    print(f"Portfolio: {out['portfolio']}")
    print(f"Valuation date: {out['valuation_date']}")
    print(f"New fund inception: {out['quality_inception']}")
    print(
        f"Max abs unit-NAV return within +/-10 days of inception: {pct(out['max_abs_window_return'])}"
    )
    print("Returns around inception:")
    for dt, ret in out["window_returns"]:
        print(f"  {dt}: {pct(ret)}")
    print(f"TWRR: {pct(out['single_twrr'])}")
    print(f"1Y Rolling Avg: {pct(out['single_roll'])}")
    print(f"Max Drawdown: {pct(out['single_dd'])}")
    print(f"Multi-benchmark completed: {out['multi_count']}")
    print(f"Skipped benchmarks: {len(out['multi_errors'])}")
    print(f"Verdict: {out['reason']}")
    if out["multi_errors"]:
        for name, err in out["multi_errors"]:
            print(f"  {name}: {err}")
    print()


def print_scenario_3(rows):
    print("SCENARIO 3: Benchmarks that nearly matched or outperformed")
    for row in rows:
        print(row["benchmark"])
        print(f"  Bench XIRR: {pct(row['bench_xirr'])}")
        print(f"  XIRR Alpha: {pct(row['alpha'])}")
        print(f"  Rolling Alpha: {pct(row['rolling_alpha'])}")
        print(f"  Upside Capture: {row['upside_capture']:.2f}x")
        print(f"  Downside Capture: {row['downside_capture']:.2f}x")
    print()


def main():
    parser = argparse.ArgumentParser(description="Stress test portfolio metric logic.")
    parser.parse_args()

    ports = load_cached_portfolios()
    registry, nav_service, simulator, compare_use_case, multi_use_case = (
        build_services()
    )

    out1 = scenario_1_same_day_boundary(
        ports, registry, nav_service, simulator, compare_use_case
    )
    out2 = scenario_2_old_new_mix(
        ports, registry, nav_service, simulator, compare_use_case, multi_use_case
    )
    out3 = scenario_3_outperforming_benchmarks(ports, registry, compare_use_case)

    print_scenario_1(out1)
    print_scenario_2(out2)
    print_scenario_3(out3)


if __name__ == "__main__":
    main()
