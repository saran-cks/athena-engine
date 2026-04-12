from typing import List, Optional
from domain.entities import Instrument

class InstrumentRegistry:
    """
    Central repository tracking available instruments (Benchmarks, Funds, ETFs).
    Initializes with hardcoded proxy codes for essential benchmarks.
    """
    def __init__(self):
        self._instruments = {
            # Existing Mutual Funds (non-index)
            "PPFAS_FLEXI": Instrument("PPFAS_FLEXI", "Parag Parikh Flexi Cap Fund - Direct Growth", "122639", "mutual_fund"),
            "SBI_GOLD": Instrument("SBI_GOLD", "SBI Gold Fund - Direct Plan", "119788", "mutual_fund"),
            "HDFC_DEFENCE": Instrument("HDFC_DEFENCE", "HDFC Defence Fund - Direct", "151750", "mutual_fund"),
            "INVESCO_FINANCIAL": Instrument("INVESCO_FINANCIAL", "Invesco India Financial Services Fund - Direct", "120385", "mutual_fund"),
            "NIPPON_ULTRA_SHORT": Instrument("NIPPON_ULTRA_SHORT", "Nippon India Ultra Short Duration Fund - Direct Plan - Growth Option", "143494", "mutual_fund"),
            "ICICI_NASDAQ_100": Instrument("ICICI_NASDAQ_100", "ICICI Prudential Nasdaq 100 Index Fund - Direct", "149219", "mutual_fund"),
            "AXIS_CHINA": Instrument("AXIS_CHINA", "Axis Greater China Equity FoF - Direct", "148699", "mutual_fund"),
            "EDELWEISS_EUROPE": Instrument("EDELWEISS_EUROPE", "Edelweiss Europe Dynamic Equity Offshore Fund - Direct", "140296", "mutual_fund"),
            "MOTILAL_MIDCAP": Instrument("MOTILAL_MIDCAP", "Motilal Oswal Midcap Fund-Direct", "127042", "mutual_fund"),
            "QUANT_SMALL": Instrument("QUANT_SMALL", "Quant small cap direct growth", "120827", "mutual_fund"),
            "SBI_BANKING": Instrument("SBI_BANKING", "SBI BANKING & FINANCIAL SERVICES FUND - DIRECT", "133859", "mutual_fund"),

            
            # The 20 Unique Index Funds
            "INDEX_NIFTY_50": Instrument("INDEX_NIFTY_50", "ICICI Prudential Nifty 50 Index Fund Direct Growth", "120620", "index_fund"),
            "INDEX_NIFTY_NEXT_50": Instrument("INDEX_NIFTY_NEXT_50", "ICICI Prudential Nifty Next 50 Index Fund Direct Growth", "120684", "index_fund"),
            "INDEX_NIFTY_100": Instrument("INDEX_NIFTY_100", "Axis Nifty 100 Index Fund - Direct Plan", "147666", "index_fund"),
            "INDEX_NIFTY_500": Instrument("INDEX_NIFTY_500", "ICICI Prudential Nifty 500 Index Fund Direct Growth", "153161", "index_fund"),
            "INDEX_MIDCAP_150": Instrument("INDEX_MIDCAP_150", "ICICI Prudential Nifty Midcap 150 Index Fund Direct Growth", "149389", "index_fund"),
            "INDEX_SMALLCAP_250": Instrument("INDEX_SMALLCAP_250", "ICICI Prudential Nifty Smallcap 250 Index Fund Direct Growth", "149283", "index_fund"),
            "INDEX_BANK": Instrument("INDEX_BANK", "ICICI Prudential Nifty Bank Index Fund Direct Growth", "149858", "index_fund"),
            "INDEX_IT": Instrument("INDEX_IT", "ICICI Prudential Nifty IT Index Fund Direct Growth", "150468", "index_fund"),
            "INDEX_PHARMA": Instrument("INDEX_PHARMA", "ICICI Prudential Nifty Pharma Index Fund Direct Growth", "150930", "index_fund"),
            "INDEX_AUTO": Instrument("INDEX_AUTO", "ICICI Prudential Nifty Auto Index Fund Direct Growth", "150643", "index_fund"),
            "INDEX_PRIVATE_BANK": Instrument("INDEX_PRIVATE_BANK", "ICICI Prudential Nifty Private Bank Index Fund Direct Growth", "153679", "index_fund"),
            "INDEX_MOMENTUM": Instrument("INDEX_MOMENTUM", "ICICI Prudential Nifty 200 Momentum 30 Index Fund Direct Growth", "150452", "index_fund"),
            "INDEX_VALUE": Instrument("INDEX_VALUE", "ICICI Prudential Nifty50 Value 20 Index Fund Direct Growth", "152365", "index_fund"),
            "INDEX_QUALITY": Instrument("INDEX_QUALITY", "ICICI Prudential Nifty200 Quality 30 Index Fund Direct Growth", "153546", "index_fund"),
            "INDEX_RAILWAYS": Instrument("INDEX_RAILWAYS", "Groww Nifty India Railways PSU Index Fund - Direct Plan", "153230", "index_fund"),
            "INDEX_NASDAQ_100_BENCH": Instrument("INDEX_NASDAQ_100_BENCH", "ICICI Prudential Nasdaq 100 Index Fund Direct Growth", "149219", "index_fund"),
            "INDEX_SP_500": Instrument("INDEX_SP_500", "Motilal Oswal S&P 500 Index Fund Direct Growth", "148381", "index_fund"),
            "INDEX_AXIS_SENSEX": Instrument("INDEX_AXIS_SENSEX", "Axis BSE Sensex Index Fund - Direct Plan", "152422", "index_fund"),
            "INDEX_SENSEX": Instrument("INDEX_SENSEX", "ICICI Prudential BSE Sensex Index Fund Direct Growth", "141841", "index_fund"),
            "INDEX_EQUAL_WEIGHT": Instrument("INDEX_EQUAL_WEIGHT", "ICICI Prudential Nifty50 Equal Weight Index Fund Direct Growth", "150639", "index_fund"),
        }
        
    def get(self, instrument_id: str) -> Optional[Instrument]:
        return self._instruments.get(instrument_id)
        
    def add(self, instrument: Instrument):
        self._instruments[instrument.instrument_id] = instrument
        
    def get_all(self) -> List[Instrument]:
        return list(self._instruments.values())
        
    def get_benchmarks(self) -> List[Instrument]:
        return [inst for inst in self._instruments.values() if inst.instrument_type == "index_fund"]
