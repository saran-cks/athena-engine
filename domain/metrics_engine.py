from typing import List, Tuple, Optional
from datetime import date
from pyxirr import xirr
from domain.entities import CashFlow
import pandas as pd
import math


class MetricsEngine:

    @staticmethod
    def calculate_xirr(cashflows: List[CashFlow]) -> float:
        if len(cashflows) < 2:
            return 0.0
        dates = [cf.date for cf in cashflows]
        amounts = [cf.amount for cf in cashflows]
        try:
            result = xirr(dates, amounts)
            return result if result is not None else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def calculate_absolute_return(invested: float, current_value: float) -> float:
        if invested <= 0:
            return 0.0
        return (current_value - invested) / invested

    @staticmethod
    def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
        if years <= 0 or start_value <= 0:
            return 0.0
        return (end_value / start_value) ** (1 / years) - 1

    @staticmethod
    def calculate_annualized_return(unit_timeline: List[Tuple[date, float]]) -> float:
        if len(unit_timeline) < 2:
            return 0.0

        start_dt, start_val = unit_timeline[0]
        end_dt, end_val = unit_timeline[-1]
        days = (end_dt - start_dt).days
        if days <= 0 or start_val <= 0 or end_val <= 0:
            return 0.0

        years = days / 365.25
        if years <= 0:
            return 0.0

        return (end_val / start_val) ** (1 / years) - 1

    @staticmethod
    def calculate_max_drawdown(nav_timeline: List[Tuple[date, float]]) -> float:
        if not nav_timeline:
            return 0.0
        max_seen = 0.0
        max_dd = 0.0
        for _, val in nav_timeline:
            if val > max_seen:
                max_seen = val
            elif max_seen > 0:
                dd = (max_seen - val) / max_seen
                if dd > max_dd:
                    max_dd = dd
        return max_dd

    @staticmethod
    def unitize_timeline(
        timeline: List[Tuple[date, float]],
        cashflows: List[CashFlow],
        tolerance_days: int = 3,
    ) -> List[Tuple[date, float]]:
        """
        Converts a portfolio value timeline into a unitized NAV series (base=100),
        stripping the effect of cash inflows so only investment returns remain.

        Key design: each inflow is consumed EXACTLY ONCE.
        Without this, a monthly SIP gets subtracted from every daily NAV point
        within the tolerance window (e.g. 3 consecutive days), causing artificial
        -3% daily returns that collapse the 1Y rolling avg to -50% to -80%.

        Matching rules:
        - Only look BACKWARD: inflow_date <= timeline_date (no future matching)
        - Within tolerance_days (for T+1/T+2 NAV settlement gaps)
        - Each inflow is marked consumed after first match; never reused
        """
        if not timeline:
            return []

        # Build sorted inflow list: (date, amount) for investments only
        inflows_by_date = {}
        for cf in cashflows:
            if cf.amount < 0:
                inflows_by_date[cf.date] = inflows_by_date.get(cf.date, 0.0) + (-cf.amount)

        inflow_list: List[Tuple[date, float]] = sorted(
            inflows_by_date.items(),
            key=lambda x: x[0],
        )
        consumed = [False] * len(inflow_list)

        def pop_nearest_inflow(target: date) -> float:
            best_idx = -1
            best_gap = tolerance_days + 1
            for i, (d, amt) in enumerate(inflow_list):
                if consumed[i]:
                    continue
                if d > target:
                    break  # sorted; no earlier uncompleted match possible
                gap = (target - d).days  # always >= 0 (backward-only)
                if gap <= tolerance_days and gap < best_gap:
                    best_gap = gap
                    best_idx = i
            if best_idx >= 0:
                consumed[best_idx] = True
                return inflow_list[best_idx][1]
            return 0.0

        unitized: List[Tuple[date, float]] = []
        nav = 100.0
        prev_val = 0.0

        for dt, val in timeline:
            inflow = pop_nearest_inflow(dt)
            if prev_val > 0:
                daily_return = (val - inflow) / prev_val - 1.0
                nav = nav * (1.0 + daily_return)
            else:
                nav = 100.0  # anchor first point, regardless of inflow
            unitized.append((dt, nav))
            prev_val = val

        return unitized

    @staticmethod
    def aggregate_portfolio_unit_nav(
        fund_value_timelines: List[List[Tuple[date, float]]],
        fund_unit_timelines: List[List[Tuple[date, float]]],
    ) -> List[Tuple[date, float]]:
        if not fund_value_timelines or not fund_unit_timelines:
            return []

        value_frames = []
        nav_frames = []

        for idx, (value_timeline, unit_timeline) in enumerate(zip(fund_value_timelines, fund_unit_timelines)):
            if not value_timeline or not unit_timeline:
                continue

            col = f"fund_{idx}"
            value_df = pd.DataFrame(value_timeline, columns=["date", col]).set_index("date")
            nav_df = pd.DataFrame(unit_timeline, columns=["date", col]).set_index("date")
            value_df.index = pd.to_datetime(value_df.index)
            nav_df.index = pd.to_datetime(nav_df.index)
            value_frames.append(value_df)
            nav_frames.append(nav_df)

        if not value_frames or not nav_frames:
            return []

        values = pd.concat(value_frames, axis=1).sort_index().ffill().fillna(0.0)
        unit_navs = pd.concat(nav_frames, axis=1).sort_index().ffill()

        fund_returns = unit_navs.pct_change(fill_method=None).fillna(0.0)
        prev_values = values.shift(1).fillna(0.0)
        prev_totals = prev_values.sum(axis=1)

        portfolio_returns = []
        for dt in values.index:
            total_prev = prev_totals.loc[dt]
            if total_prev <= 0:
                portfolio_returns.append(0.0)
                continue

            weights = prev_values.loc[dt] / total_prev
            fund_ret_row = fund_returns.loc[dt].reindex(weights.index).fillna(0.0)
            portfolio_returns.append(float((weights * fund_ret_row).sum()))

        portfolio_nav = []
        nav = 100.0
        for dt, port_ret in zip(values.index, portfolio_returns):
            nav *= (1.0 + port_ret)
            portfolio_nav.append((dt.date(), nav))

        return portfolio_nav

    @staticmethod
    def calculate_rolling_and_capture_from_nav(
        actual_nav: List[Tuple[date, float]],
        benchmark_nav: List[Tuple[date, float]],
    ) -> Tuple[float, Optional[float], Optional[float], Optional[float], Optional[float]]:
        if len(benchmark_nav) < 30:
            act_roll = MetricsEngine._calc_1y_rolling_avg(actual_nav)
            return act_roll, None, None, None, None

        act_roll = MetricsEngine._calc_1y_rolling_avg(actual_nav)
        ben_roll = MetricsEngine._calc_1y_rolling_avg(benchmark_nav)
        
        rolling_alpha = None
        if act_roll is not None and ben_roll is not None:
            rolling_alpha = act_roll - ben_roll

        uc, dc = MetricsEngine._calc_capture_ratios(actual_nav, benchmark_nav)
        return act_roll, ben_roll, rolling_alpha, uc, dc

    @staticmethod
    def _calc_1y_rolling_avg(unit_timeline: List[Tuple[date, float]]) -> Optional[float]:
        if len(unit_timeline) < 2:
            return None
        returns = []
        n = len(unit_timeline)
        for i in range(n):
            start_dt, start_val = unit_timeline[i]
            try:
                target_dt = start_dt.replace(year=start_dt.year + 1)
            except ValueError:
                target_dt = start_dt.replace(year=start_dt.year + 1, day=28)
            for j in range(i + 1, n):
                if unit_timeline[j][0] >= target_dt:
                    end_val = unit_timeline[j][1]
                    if start_val > 0:
                        returns.append((end_val - start_val) / start_val)
                    break
        return sum(returns) / len(returns) if returns else None

    @staticmethod
    def _calc_capture_ratios(
        port_nav: List[Tuple[date, float]],
        bench_nav: List[Tuple[date, float]],
    ) -> Tuple[float, float]:
        if not port_nav or not bench_nav:
            return 0.0, 0.0

        df_p = pd.DataFrame(port_nav, columns=["date", "p_nav"]).set_index("date")
        df_b = pd.DataFrame(bench_nav, columns=["date", "b_nav"]).set_index("date")
        df_p.index = pd.to_datetime(df_p.index)
        df_b.index = pd.to_datetime(df_b.index)

        df = df_p.join(df_b, how="outer").sort_index().ffill().dropna()
        if df.empty:
            return 0.0, 0.0

        df_monthly = df.resample("ME").last()
        returns = df_monthly.pct_change().dropna()

        if returns.empty:
            return 0.0, 0.0

        up_months = returns[returns["b_nav"] > 0]
        down_months = returns[returns["b_nav"] < 0]

        uc = MetricsEngine._capture_ratio_from_bucket(up_months)
        dc = MetricsEngine._capture_ratio_from_bucket(down_months)
        return uc, dc

    @staticmethod
    def _capture_ratio_from_bucket(
        bucket: pd.DataFrame,
    ) -> float:
        if bucket.empty:
            return 0.0

        port_linked = math.prod(1.0 + r for r in bucket["p_nav"]) - 1.0
        bench_linked = math.prod(1.0 + r for r in bucket["b_nav"]) - 1.0

        if abs(bench_linked) < 1e-12:
            return 0.0
        return port_linked / bench_linked

    @staticmethod
    def calculate_alpha(actual_xirr: float, benchmark_xirr: float) -> float:
        return actual_xirr - benchmark_xirr

    # --- Extensibility Hooks --- #
    @staticmethod
    def calculate_rolling_xirr():
        pass

    @staticmethod
    def calculate_sharpe_ratio():
        pass
