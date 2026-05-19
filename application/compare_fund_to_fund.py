from typing import List, Tuple
from domain.entities import Instrument, SimulationResult, Transaction
from domain.investment_simulator import InvestmentSimulator
from domain.metrics_engine import MetricsEngine


class CompareFundToFund:
    def __init__(self, simulator: InvestmentSimulator):
        self.simulator = simulator

    def execute(
        self, transactions_a: List[Transaction], fund_a: Instrument, fund_b: Instrument
    ) -> Tuple[SimulationResult, SimulationResult, float, float]:
        """
        Takes Fund A's historical transaction file and simulates them exactly
        on Fund B to allow a precise unit-for-unit comparison.
        Returns: Sim A, Sim B, XIRR A, XIRR B
        """
        # Simulate A reality
        sim_a = self.simulator.simulate(transactions_a, fund_a)

        # Map transactions to B
        txs_b = [
            Transaction(
                date=tx.date,
                amount=tx.amount,
                instrument_id=fund_b.instrument_id,
                portfolio_id=tx.portfolio_id,
            )
            for tx in transactions_a
        ]

        # Simulate B proxy
        sim_b = self.simulator.simulate(txs_b, fund_b)

        xirr_a = MetricsEngine.calculate_xirr(sim_a.cashflows)
        xirr_b = MetricsEngine.calculate_xirr(sim_b.cashflows)

        return sim_a, sim_b, xirr_a, xirr_b
