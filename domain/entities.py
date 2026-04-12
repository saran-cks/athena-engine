from dataclasses import dataclass, field
from datetime import date
from typing import Literal, List, Tuple

@dataclass
class Instrument:
    instrument_id: str
    name: str
    scheme_code: str
    instrument_type: Literal["mutual_fund", "index_fund", "etf"]

@dataclass
class Transaction:
    date: date
    amount: float  # positive = investment (cash outflow from investor)
    instrument_id: str
    portfolio_id: str

@dataclass
class Portfolio:
    portfolio_id: str
    owner: str
    transactions: List[Transaction]

@dataclass
class CashFlow:
    """
    Represents a physical cash flow on a date.
    Negative = Cash outflow from investor (e.g., buying units).
    Positive = Cash inflow to investor (e.g., selling units, or final portfolio valuation).
    """
    date: date
    amount: float

@dataclass
class SimulationResult:
    instrument: Instrument
    total_units: float
    invested_amount: float
    current_value: float
    cashflows: List[CashFlow]
    timeline_nav: List[Tuple[date, float]]           # (Date, NAV on that date)
    portfolio_value_timeline: List[Tuple[date, float]] # (Date, Value of portfolio on that date)

@dataclass
class ComparisonResult:
    portfolio_id: str
    benchmark: Instrument
    actual_xirr: float
    benchmark_xirr: float
    alpha: float
    actual_value: float
    benchmark_value: float
    total_invested: float
    actual_cagr: float = 0.0
    benchmark_cagr: float = 0.0
    actual_abs_return: float = 0.0
    benchmark_abs_return: float = 0.0
    actual_max_dd: float = 0.0
    benchmark_max_dd: float = 0.0
    actual_1y_rolling: float = 0.0
    benchmark_1y_rolling: float = 0.0
    rolling_alpha: float = 0.0
    upside_capture: float = 0.0
    downside_capture: float = 0.0
    actual_timeline: List[Tuple[date, float]] = None
    benchmark_timeline: List[Tuple[date, float]] = None
    actual_contributions: dict = field(default_factory=dict)
