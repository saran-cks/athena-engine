import re
from typing import Dict, List, Optional
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
        self._active_analysis_specs: Dict[str, Dict[str, str]] = {
            "ACTIVE_PPFAS_FLEXI": {
                "name": "Parag Parikh Flexi Cap Fund",
                "lookup_name": "Parag Parikh Flexi Cap Fund - Direct Growth",
                "scheme_code": "122639",
            },
            "ACTIVE_HDFC_FLEXI": {
                "name": "HDFC Flexi Cap Fund",
                "lookup_name": "HDFC Flexi Cap Fund - Growth Option - Direct Plan",
                "scheme_code": "118955",
            },
            "ACTIVE_ICICI_FLEXICAP": {
                "name": "ICICI Prudential Flexicap Fund",
                "lookup_name": "ICICI Prudential Flexicap Fund - Direct Plan - Growth",
                "scheme_code": "148990",
            },
            "ACTIVE_HDFC_MIDCAP": {
                "name": "HDFC Mid-Cap Opportunities Fund",
                "lookup_name": "HDFC Mid-Cap Opportunities Fund - Growth Option - Direct Plan",
                "scheme_code": "118989",
            },
            "ACTIVE_NIPPON_GROWTH": {
                "name": "Nippon India Growth Mid Cap Fund",
                "lookup_name": "Nippon India Growth Mid Cap Fund - Direct Plan Growth Plan - Growth Option",
                "scheme_code": "118668",
            },
            "ACTIVE_MOTILAL_MIDCAP": {
                "name": "Motilal oswal midcap fund direct",
                "lookup_name": "Motilal Oswal Midcap Fund - Direct Plan - Growth Option",
                "scheme_code": "127042",
            },
            "ACTIVE_ICICI_LARGEMID": {
                "name": "ICICI Prudential Large & Mid Cap Fund",
                "lookup_name": "ICICI Prudential Large & Mid Cap Fund - Direct Plan - Growth",
                "scheme_code": "120596",
            },
            "ACTIVE_MOTILAL_LARGEMID": {
                "name": "Motilal Oswal Large & Midcap Fund",
                "lookup_name": "Motilal Oswal Large and Midcap Fund - Direct Plan - Growth Option",
                "scheme_code": "147704",
            },
            "ACTIVE_QUANT_FLEXI": {
                "name": "Quant Flexi Cap Fund",
                "lookup_name": "Quant Flexi Cap Fund - Direct Plan - Growth Option",
                "scheme_code": "120843",
            },
            "ACTIVE_SBI_CONTRA": {
                "name": "SBI Contra Fund",
                "lookup_name": "SBI Contra Fund - Direct Plan - Growth",
                "scheme_code": "119835",
            },
            "ACTIVE_EDELWEISS_EMERGING": {
                "name": "Edelweiss Emerging Markets Opportunities Equity Offshore Fund Direct Growth",
                "lookup_name": "Edelweiss Emerging Markets Opportunities Equity Offshore Fund - Direct Plan - Growth Option",
                "scheme_code": "140327",
            },
            "ACTIVE_FRANKLIN_CORP_DEBT": {
                "name": "Franklin India Corporate Debt Fund Direct Growth",
                "lookup_name": "Franklin India Corporate Debt Fund - Direct - Growth",
                "scheme_code": "118569",
            },
            "ACTIVE_NIPPON_TAIWAN": {
                "name": "Nippon India Taiwan Equity Fund Direct Growth",
                "lookup_name": "Nippon India Taiwan Equity Fund - Direct Plan - Growth Option",
                "scheme_code": "149329",
            },
            "ACTIVE_EDELWEISS_AGGR_HYBRID": {
                "name": "Edelweiss Aggressive Hybrid Fund Direct Growth",
                "lookup_name": "Edelweiss Aggressive Hybrid Fund - Direct Plan - Growth Option",
                "scheme_code": "118624",
            },
            "ACTIVE_ABSL_CREDIT_RISK": {
                "name": "Aditya Birla Sun Life Credit Risk Fund Direct Growth",
                "lookup_name": "Aditya Birla Sun Life Credit Risk Fund - Growth - Direct Plan",
                "scheme_code": "134387",
            },
            "ACTIVE_AXIS_GLOBAL_ALPHA": {
                "name": "Axis Global Equity Alpha FoF Direct Growth",
                "lookup_name": "Axis Global Equity Alpha Fund of Fund - Direct Plan - Growth",
                "scheme_code": "134387",
            },
            "ACTIVE_SBI_BANKING": {
                "name": "SBI Banking & Financial Services Fund Direct Growth",
                "lookup_name": "SBI BANKING & FINANCIAL SERVICES FUND - DIRECT",
                "scheme_code": "133859",
            },
            "ACTIVE_ICICI_PHD": {
                "name": "ICICI Prudential Pharma Healthcare and Diagnostics (P.H.D) Fund Direct Growth",
                "lookup_name": "ICICI Prudential Pharma Healthcare and Diagnostics (P.H.D) Fund - Direct Plan - Growth",
                "scheme_code": "143874",
            },
            "ACTIVE_BANDHAN_SMALLCAP": {
                "name": "Bandhan small cap fund",
                "lookup_name": "Bandhan Small Cap Fund - Direct Plan - Growth",
                "scheme_code": "147946",
            },
             "ACTIVE_HSBC_NIFTY": {
                "name": "HSBC Nifty 50 Index Fund Direct Growth",
                "lookup_name": "HSBC Nifty 50 Index Fund Direct Growth",
                "scheme_code": "151157",
            },
              "ACTIVE_HSBC_NEXT_NIFTY": {
                "name": "HSBC Next Nifty 50 Index Fund Direct Growth",
                "lookup_name": "HSBC Next Nifty 50 Index Fund Direct Growth",
                "scheme_code": "151160",
            },
             "ACTIVE_SBI_GOLD": {
                "name": "SBI GOLD FUND",
                "lookup_name": "SBI GOLD FUND",
                "scheme_code": "119788",
            },
        }
        self._active_analysis_ids = list(self._active_analysis_specs.keys())
        self._amfi_lookup_cache = None

        for instrument_id, spec in self._active_analysis_specs.items():
            self._instruments[instrument_id] = Instrument(
                instrument_id,
                spec["name"],
                spec["scheme_code"],
                "mutual_fund",
            )
        
    def get(self, instrument_id: str) -> Optional[Instrument]:
        return self._instruments.get(instrument_id)
        
    def add(self, instrument: Instrument):
        self._instruments[instrument.instrument_id] = instrument
        
    def get_all(self) -> List[Instrument]:
        return list(self._instruments.values())
        
    def get_benchmarks(self) -> List[Instrument]:
        return [inst for inst in self._instruments.values() if inst.instrument_type == "index_fund"]

    def get_active_funds_for_analysis(self) -> List[Instrument]:
        return [self._instruments[instrument_id] for instrument_id in self._active_analysis_ids]

    def resolve_missing_scheme_codes(self, amfi_client, instruments: Optional[List[Instrument]] = None) -> List[str]:
        targets = instruments if instruments is not None else list(self._instruments.values())
        unresolved = []

        scheme_lookup = None
        for instrument in targets:
            if instrument.scheme_code:
                continue

            if scheme_lookup is None:
                scheme_lookup = self._get_amfi_lookup(amfi_client)
                if not scheme_lookup:
                    unresolved.append(instrument.name)
                    continue

            resolved_code = self._resolve_scheme_code_from_lookup(instrument, scheme_lookup)
            if resolved_code:
                instrument.scheme_code = resolved_code
            else:
                unresolved.append(instrument.name)

        return unresolved

    def _get_amfi_lookup(self, amfi_client):
        if self._amfi_lookup_cache is not None:
            return self._amfi_lookup_cache

        df = amfi_client.fetch_daily_all()
        if df is None or df.empty:
            return []

        direct_growth_rows = []
        for row in df.itertuples(index=False):
            scheme_name = str(row.scheme_name)
            compact_name = self._compact_text(scheme_name)
            direct_growth_rows.append({
                "scheme_code": str(row.scheme_code),
                "scheme_name": scheme_name,
                "compact_name": compact_name,
                "is_direct_growth": "direct" in compact_name and "growth" in compact_name,
            })

        self._amfi_lookup_cache = direct_growth_rows
        return self._amfi_lookup_cache

    def _resolve_scheme_code_from_lookup(self, instrument: Instrument, scheme_lookup) -> Optional[str]:
        lookup_name = self._active_analysis_specs.get(instrument.instrument_id, {}).get("lookup_name", instrument.name)
        lookup_compact = self._compact_text(lookup_name)
        name_compact = self._compact_text(instrument.name)

        direct_growth_candidates = [
            row for row in scheme_lookup
            if row["is_direct_growth"] and (lookup_compact in row["compact_name"] or name_compact in row["compact_name"])
        ]
        if direct_growth_candidates:
            return self._pick_best_candidate(lookup_compact, direct_growth_candidates)

        any_candidates = [
            row for row in scheme_lookup
            if lookup_compact in row["compact_name"] or name_compact in row["compact_name"]
        ]
        if any_candidates:
            return self._pick_best_candidate(lookup_compact, any_candidates)

        return None

    def _pick_best_candidate(self, lookup_compact: str, candidates) -> str:
        best_row = max(
            candidates,
            key=lambda row: (
                row["compact_name"] == lookup_compact,
                lookup_compact in row["compact_name"],
                row["is_direct_growth"],
                len(lookup_compact) / max(len(row["compact_name"]), 1),
            ),
        )
        return best_row["scheme_code"]

    @staticmethod
    def _compact_text(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower())
