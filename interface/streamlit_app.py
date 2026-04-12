import streamlit as st
import pandas as pd
from datetime import date
import sys
import os
from urllib.parse import quote

# Add root project directory to path to allow importing layers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Service initialization
from data_layer.amfi_client import AmfiClient
from data_layer.nav_repository import NavRepository
from data_layer.nav_store import NavStore
from data_layer.transaction_repository import TransactionRepository
from data_layer.instrument_registry import InstrumentRegistry
from domain.nav_service import NavService
from domain.investment_simulator import InvestmentSimulator
from domain.portfolio_aggregator import PortfolioAggregator
from domain.metrics_engine import MetricsEngine
from domain.benchmark_comparator import BenchmarkComparator
from application.compare_portfolio_to_benchmark import ComparePortfolioToBenchmark
from application.compare_fund_to_fund import CompareFundToFund
from application.compare_multiple_portfolios import CompareMultiplePortfolios
from application.multi_benchmark_analysis import MultiBenchmarkAnalysis
from domain.entities import Portfolio, Transaction

st.set_page_config(page_title="Athena - MF Engine", layout="wide")


def build_athena_backdrop() -> str:
    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1100">
      <defs>
        <linearGradient id="mist" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#f5d88b" stop-opacity="0.15"/>
          <stop offset="45%" stop-color="#d1b26f" stop-opacity="0.08"/>
          <stop offset="100%" stop-color="#5c6577" stop-opacity="0.02"/>
        </linearGradient>
        <radialGradient id="halo" cx="52%" cy="30%" r="42%">
          <stop offset="0%" stop-color="#f5e0a4" stop-opacity="0.18"/>
          <stop offset="35%" stop-color="#d8b46a" stop-opacity="0.08"/>
          <stop offset="100%" stop-color="#0e1420" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect width="1600" height="1100" fill="url(#mist)"/>
      <rect width="1600" height="1100" fill="url(#halo)"/>
      <g transform="translate(805 130)" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M0 28 C66 38 117 84 132 142 C144 190 134 258 92 304 C59 340 18 365 -24 380 C-70 397 -123 401 -171 385 C-223 367 -274 328 -302 273 C-329 221 -334 155 -310 105 C-285 54 -238 18 -179 7 C-137 -1 -93 0 -53 11 C-32 -14 -6 -33 24 -46 C77 -69 132 -72 182 -58 C235 -43 283 -6 309 46 C339 107 331 182 287 233"
              stroke="#e2c27a" stroke-width="18" opacity="0.22"/>
        <path d="M-64 30 C-26 -17 39 -48 108 -44 C172 -39 232 -7 269 40 C308 89 323 158 306 224 C291 285 252 333 200 364 C167 384 131 396 97 398"
              stroke="#f5deb0" stroke-width="9" opacity="0.18"/>
        <path d="M-82 101 L-15 30 L40 104" stroke="#f2d594" stroke-width="14" opacity="0.16"/>
        <path d="M-10 33 L-10 124" stroke="#f2d594" stroke-width="10" opacity="0.16"/>
        <path d="M-158 238 C-114 180 -41 151 28 165 C105 181 169 245 183 325 C198 406 166 488 101 535 C40 580 -51 591 -127 563 C-203 536 -260 474 -272 397 C-285 313 -244 237 -178 202"
              stroke="#d8bb7a" stroke-width="13" opacity="0.16"/>
        <path d="M-27 180 C8 229 10 284 -2 350 C-14 419 -47 489 -98 543"
              stroke="#e8cf98" stroke-width="8" opacity="0.14"/>
        <path d="M107 223 C188 251 245 330 252 412 C260 507 194 608 103 641"
              stroke="#b6c4d8" stroke-width="7" opacity="0.12"/>
        <circle cx="-39" cy="245" r="9" fill="#e8cf98" opacity="0.18"/>
        <circle cx="45" cy="247" r="9" fill="#e8cf98" opacity="0.18"/>
        <path d="M-132 551 C-172 635 -205 742 -210 843" stroke="#d9c086" stroke-width="16" opacity="0.13"/>
        <path d="M-44 558 C-49 671 -52 783 -50 893" stroke="#f4e0b1" stroke-width="12" opacity="0.10"/>
        <path d="M88 535 C116 624 137 719 149 823" stroke="#9fb0c8" stroke-width="14" opacity="0.10"/>
        <path d="M196 382 C278 344 346 289 390 213" stroke="#f0d08a" stroke-width="12" opacity="0.12"/>
        <path d="M380 215 L426 123" stroke="#f0d08a" stroke-width="13" opacity="0.12"/>
        <path d="M360 250 L453 229" stroke="#f0d08a" stroke-width="11" opacity="0.11"/>
      </g>
    </svg>
    """
    return f"data:image/svg+xml;utf8,{quote(svg)}"


def inject_theme():
    backdrop = build_athena_backdrop()
    st.markdown(
        f"""
        <style>
        :root {{
            --athena-bg: #0a1018;
            --athena-panel: rgba(11, 18, 28, 0.76);
            --athena-panel-strong: rgba(14, 22, 34, 0.88);
            --athena-border: rgba(229, 194, 116, 0.16);
            --athena-accent: #e5c274;
            --athena-accent-soft: #f3dfb1;
            --athena-ink: #edf3fb;
            --athena-muted: #8d9aac;
            --athena-grid: rgba(229, 194, 116, 0.06);
        }}

        .stApp {{
            background:
                linear-gradient(180deg, rgba(6, 10, 18, 0.98), rgba(7, 12, 20, 0.94)),
                radial-gradient(circle at top left, rgba(229, 194, 116, 0.08), transparent 30%),
                var(--athena-bg);
            color: var(--athena-ink);
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background-image: url("{backdrop}");
            background-repeat: no-repeat;
            background-position: center 5rem;
            background-size: min(1050px, 88vw);
            opacity: 0.28;
            pointer-events: none;
            z-index: 0;
            filter: saturate(0.9) contrast(1.03);
        }}

        .stApp::after {{
            content: "";
            position: fixed;
            inset: 0;
            background:
                linear-gradient(transparent 0%, rgba(7, 11, 18, 0.52) 65%, rgba(7, 11, 18, 0.88) 100%),
                repeating-linear-gradient(
                    90deg,
                    transparent 0,
                    transparent 95px,
                    var(--athena-grid) 96px
                );
            pointer-events: none;
            z-index: 0;
            opacity: 0.5;
        }}

        [data-testid="stAppViewContainer"] > .main {{
            position: relative;
            z-index: 1;
        }}

        [data-testid="stHeader"] {{
            background: rgba(8, 12, 20, 0.58);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(229, 194, 116, 0.08);
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(8, 13, 22, 0.96), rgba(11, 18, 28, 0.94));
            border-right: 1px solid rgba(229, 194, 116, 0.08);
        }}

        .block-container {{
            padding-top: 2.4rem;
            padding-bottom: 3rem;
        }}

        .athena-hero {{
            position: relative;
            overflow: hidden;
            padding: 1.2rem 1.25rem 1.1rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--athena-border);
            border-radius: 22px;
            background:
                linear-gradient(135deg, rgba(17, 26, 40, 0.88), rgba(8, 14, 22, 0.72)),
                radial-gradient(circle at top right, rgba(229, 194, 116, 0.12), transparent 35%);
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.24);
            backdrop-filter: blur(12px);
        }}

        .athena-hero::after {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, transparent, rgba(229, 194, 116, 0.05), transparent);
            transform: translateX(-100%);
            animation: athenaSheen 10s linear infinite;
        }}

        @keyframes athenaSheen {{
            to {{ transform: translateX(100%); }}
        }}

        .athena-eyebrow {{
            letter-spacing: 0.22em;
            text-transform: uppercase;
            font-size: 0.76rem;
            color: var(--athena-accent);
            margin-bottom: 0.4rem;
            font-weight: 700;
        }}

        .athena-title {{
            font-size: clamp(2rem, 3.6vw, 3.4rem);
            line-height: 0.95;
            font-weight: 800;
            color: #f7f5ef;
            margin: 0;
        }}

        .athena-subtitle {{
            margin-top: 0.55rem;
            max-width: 62rem;
            color: #b2becc;
            font-size: 0.98rem;
            line-height: 1.5;
        }}

        h1, h2, h3 {{
            color: #f5f7fb;
            letter-spacing: -0.02em;
        }}

        [data-testid="stMetric"] {{
            padding: 1rem 1rem 0.9rem;
            border-radius: 18px;
            background: linear-gradient(180deg, var(--athena-panel), rgba(9, 14, 24, 0.66));
            border: 1px solid rgba(229, 194, 116, 0.10);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
            backdrop-filter: blur(8px);
        }}

        [data-testid="stMetricLabel"] {{
            color: var(--athena-muted);
            font-weight: 600;
            letter-spacing: 0.02em;
        }}

        [data-testid="stMetricValue"] {{
            color: #f9fbff;
        }}

        .stButton > button, .stDownloadButton > button {{
            border-radius: 999px;
            border: 1px solid rgba(229, 194, 116, 0.24);
            background: linear-gradient(180deg, rgba(33, 45, 62, 0.9), rgba(16, 24, 38, 0.95));
            color: #f6f3ea;
            padding: 0.45rem 1rem;
        }}

        .stButton > button:hover, .stDownloadButton > button:hover {{
            border-color: rgba(229, 194, 116, 0.42);
            color: white;
        }}

        .stSelectbox > div > div,
        .stTextInput > div > div > input,
        .stFileUploader,
        [data-testid="stDataFrame"] {{
            background: var(--athena-panel-strong);
            border-radius: 16px;
        }}

        [data-testid="stMarkdownContainer"] p,
        .stCaption {{
            color: #c0cad8;
        }}

        hr {{
            border-color: rgba(229, 194, 116, 0.09);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_shell(title: str, subtitle: str):
    st.markdown(
        f"""
        <section class="athena-hero">
            <div class="athena-eyebrow">Athena Tactical Wealth Intelligence</div>
            <h1 class="athena-title">{title}</h1>
            <div class="athena-subtitle">{subtitle}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


inject_theme()

def get_services():
    client = AmfiClient()
    repo = NavRepository("db/nav_cache.db")
    store = NavStore("db/nav_cache.db")
    tx_repo = TransactionRepository()
    registry = InstrumentRegistry()
    nav_s = NavService(store)
    sim = InvestmentSimulator(nav_s)
    agg = PortfolioAggregator()
    comp = BenchmarkComparator(sim)
    
    uc_p2b = ComparePortfolioToBenchmark(registry, sim, agg, comp)
    uc_f2f = CompareFundToFund(sim)
    uc_mp = CompareMultiplePortfolios(uc_p2b)
    uc_mb = MultiBenchmarkAnalysis(uc_p2b)
    
    return client, repo, tx_repo, registry, uc_p2b, uc_f2f, uc_mp, uc_mb

client, repo, tx_repo, registry, uc_p2b, uc_f2f, uc_mp, uc_mb = get_services()

import pickle

PORT_CACHE_PATH = "db/portfolio_cache.pkl"

def save_portfolios():
    with open(PORT_CACHE_PATH, "wb") as f:
        pickle.dump(st.session_state.portfolios, f)

if "portfolios" not in st.session_state:
    if os.path.exists(PORT_CACHE_PATH):
        try:
            with open(PORT_CACHE_PATH, "rb") as f:
                st.session_state.portfolios = pickle.load(f)
        except Exception:
            st.session_state.portfolios = {}
    else:
        st.session_state.portfolios = {}

def format_perc(val):
    if val is None:
        return "N/A"
    return f"{val*100:.2f}%"

def format_curr(val):
    if val is None:
        return "N/A"
    return f"₹{val:,.0f}"

def format_capture(val):
    if val is None:
        return "N/A"
    if val < 0:
        return f"{val:.2f}x ⚡"
    return f"{val:.2f}x"

# --- PAGES --- #

def page_data_setup():
    render_shell(
        "Fire of Prometheus",
        "Wire up instruments, sync NAV history, and stage portfolios for disciplined benchmark analysis.",
    )
    st.title("Data Setup")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sync NAV Data")
        if st.button("Sync AMFI Daily (All Funds)"):
            with st.spinner("Downloading NAVAll.txt..."):
                df = client.fetch_daily_all()
                if df is not None:
                    records = [(r['scheme_code'], r['date'], r['nav']) for _, r in df.iterrows()]
                    repo.upsert_bulk(records)
                    st.success(f"Synced {len(records)} records for today.")
                else:
                    st.error("Failed to sync.")
                    
    with col2:
        st.subheader("Database Setup")
        st.markdown("**Sync Full History for ALL Funds (Required for Simulation)**")
        st.info("Fetches all multi-year history for all registered funds natively via MFAPI exactly once.")
        if st.button("Sync All Funds Data"):
            with st.spinner("Downloading histories... this may take a bit for a large list"):
                for inst_id, inst in registry._instruments.items():
                    hist = client.fetch_history(inst.scheme_code)
                    if hist:
                        repo.insert_mfapi_history(inst.scheme_code, hist)
            st.success("All funds perfectly synchronized!")
            
    st.divider()
    
    st.subheader("Upload Portfolios")
    st.info("💡 To combine multiple funds into a single Portfolio, simply upload them one-by-one using the EXACT SAME Portfolio Name!")
    
    colA, colB = st.columns(2)
    with colA:
        port_id = st.text_input("Portfolio Name (e.g. My_SIPs)", value="Default_Port")
        bench_names = {b.name: b for b in registry.get_all()}
        fund_name = st.selectbox("Map file to Instrument:", list(bench_names.keys()))
    with colB:
        files = st.file_uploader("Upload CSV/XLSX (date, amount)", accept_multiple_files=True)
        if st.button("Load Transaction Files"):
            inst = bench_names[fund_name]
            for file in files:
                try:
                    txs = tx_repo.load_from_file(file, file.name, inst.instrument_id, port_id)
                    if port_id not in st.session_state.portfolios:
                        st.session_state.portfolios[port_id] = Portfolio(portfolio_id=port_id, owner="User", transactions=[])
                    st.session_state.portfolios[port_id].transactions.extend(txs)
                    save_portfolios()
                    st.success(f"Loaded {len(txs)} txs from {file.name}")
                except Exception as e:
                    st.error(f"Error parsing file: {e}")
                    
        st.divider()
        st.write("Current Portfolios in memory:")
        for k, v in list(st.session_state.portfolios.items()):
            rcol1, rcol2 = st.columns([3, 1])
            rcol1.write(f"- **{k}**: {len(v.transactions)} total transactions")
            if rcol2.button("🗑️ Delete", key=f"del_{k}"):
                del st.session_state.portfolios[k]
                save_portfolios()
                st.rerun()

def page_single_analysis(hide_title=False):
    if not hide_title:
        render_shell(
            "Theatre of Dionysus",
            "Pressure-test a live portfolio against a chosen benchmark using money-weighted returns, path diagnostics, and simulation overlays.",
        )
        st.title("Single Portfolio vs Benchmark")
        
    if not st.session_state.portfolios:
        st.warning("Upload a portfolio first.")
        return
        
    p_name = st.selectbox("Select Portfolio", list(st.session_state.portfolios.keys()))
    benchmaps = {b.name: b for b in registry.get_benchmarks()}
    b_name = st.selectbox("Select Benchmark", list(benchmaps.keys()))
    
    if st.button("Analyze"):
        try:
            port = st.session_state.portfolios[p_name]
            bench = benchmaps[b_name]
            res = uc_p2b.execute(port, bench)
            
            # Metrics
            st.subheader("Metrics vs Benchmark")
            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
            kpi1.metric("Actual XIRR", format_perc(res.actual_xirr))
            kpi2.metric(f"Bench XIRR", format_perc(res.benchmark_xirr))
            kpi3.metric("Alpha", format_perc(res.alpha), delta_color="normal" if res.alpha > 0 else "inverse")
            kpi4.metric("Actual Value", format_curr(res.actual_value))
            kpi5.metric("Total Invested", format_curr(res.total_invested))
            
            st.divider()
            colA, colB = st.columns(2)
            with colA:
                st.subheader("📈 Advanced Actual Metrics")
                st.metric("Annualized Return (TWRR)", format_perc(res.actual_cagr))
                st.metric("1Y Rolling Avg", format_perc(res.actual_1y_rolling))
                st.metric("Absolute Return", format_perc(res.actual_abs_return))
                st.metric("Max Drawdown", format_perc(res.actual_max_dd), delta_color="inverse")
            with colB:
                st.subheader("🤖 Simulated Benchmark Metrics")
                st.metric("Annualized Return (TWRR)", format_perc(res.benchmark_cagr))
                st.metric("1Y Rolling Avg", format_perc(res.benchmark_1y_rolling))
                
                est_income = (res.benchmark_value - res.total_invested) if (res.benchmark_value is not None and res.total_invested is not None) else None
                st.metric("Est. Bench Income", format_curr(est_income))
                
                st.metric("Absolute Return", format_perc(res.benchmark_abs_return))
                st.metric("Max Drawdown", format_perc(res.benchmark_max_dd), delta_color="inverse")
                
            st.divider()
            colX, colY, colZ = st.columns(3)
            with colX:
                st.metric("Rolling Alpha (Unitized)", format_perc(res.rolling_alpha))
            with colY:
                st.metric("Upside Capture Ratio", format_capture(res.upside_capture))
            with colZ:
                st.metric("Downside Capture Ratio", format_capture(res.downside_capture), delta_color="inverse")
                
            if len(res.actual_contributions) > 1:
                st.divider()
                st.subheader("Portfolio Asset Contribution Breakdown")
                pie_df = pd.DataFrame(list(res.actual_contributions.items()), columns=["Fund", "Current Value"])
                import altair as alt
                fig = alt.Chart(pie_df).mark_arc(innerRadius=50).encode(
                    theta="Current Value",
                    color="Fund",
                    tooltip=["Fund", "Current Value"]
                )
                st.altair_chart(fig)
            
            st.divider()
            st.subheader("Portfolio Value Growth Over Time")
            
            # Build DataFrame for charting
            if res.actual_timeline and res.benchmark_timeline:
                # Merge timelines by date
                df_act = pd.DataFrame(res.actual_timeline, columns=["Date", "Actual Portfolio"])
                df_bench = pd.DataFrame(res.benchmark_timeline, columns=["Date", "Benchmark Simulation"])
                df_act.set_index("Date", inplace=True)
                df_bench.set_index("Date", inplace=True)
                
                # Outer join to ensure dates line up, ffill missing
                df_plot = df_act.join(df_bench, how="outer").ffill().fillna(0.0)
                st.line_chart(df_plot, color=["#1f77b4", "#2ca02c"])
            else:
                st.info("Chart plotting requires historical simulation data.")
                
        except Exception as e:
            st.error(f"Execution failed: {e}. Check if data/history is fully synced.")

def page_portfolio_analysis():
    render_shell(
        "Cerberus the Hound",
        "Study a multi-asset portfolio as one coordinated system with flow-aware analytics and benchmark context.",
    )
    st.title("Portfolio Analysis")
    st.info("Since portfolios natively accept multiple funds in our architecture, this executes just like Single Analysis but aggregates underlying assets seamlessly.")
    page_single_analysis(hide_title=True)

def page_multi_benchmark():
    render_shell(
        "Wisdom of Athena",
        "Run the same portfolio through the full benchmark field to see where performance is structural, cyclical, or accidental.",
    )
    st.title("Multi-Benchmark Analysis")
    if not st.session_state.portfolios:
        st.warning("Upload a portfolio first.")
        return
        
    p_name = st.selectbox("Select Portfolio to Benchmark", list(st.session_state.portfolios.keys()))
    benchmarks = registry.get_benchmarks()
    
    if st.button("Run Multi-Analysis"):
        port = st.session_state.portfolios[p_name]
        try:
            results = uc_mb.execute(port, benchmarks)
            skipped = getattr(uc_mb, "last_errors", [])

            if not results:
                if skipped:
                    details = "\n".join([f"- {name}: {msg}" for name, msg in skipped])
                    st.error(f"No benchmark analyses could be completed.\n{details}")
                else:
                    st.error("No benchmark analyses could be completed.")
                return
            
            # Build a comparative table
            table_data = []
            for r in results:
                b_income = (r.benchmark_value - r.total_invested) if (r.benchmark_value is not None and r.total_invested is not None) else None
                table_data.append({
                    "Benchmark": r.benchmark.name,
                    "Alpha": format_perc(r.alpha),
                    "Bench XIRR": format_perc(r.benchmark_xirr),
                    "Rolling Alpha": format_perc(r.rolling_alpha),
                    "Up Cap": format_capture(r.upside_capture),
                    "Down Cap": format_capture(r.downside_capture),
                    "Est. Bench Income": format_curr(b_income),
                    "Bench Final Value": format_curr(r.benchmark_value),
                    "Bench Max DD": format_perc(r.benchmark_max_dd)
                })
            
            # actual is identical across all results
            actual_xirr = results[0].actual_xirr
            actual_val = results[0].actual_value
            
            st.subheader(f"Baseline Portfolio -> XIRR: {format_perc(actual_xirr)} | Value: {format_curr(actual_val)}")
            st.dataframe(pd.DataFrame(table_data))

            if skipped:
                details = "\n".join([f"- {name}: {msg}" for name, msg in skipped])
                st.warning(f"Skipped {len(skipped)} benchmark(s) due to missing or stale NAV history:\n{details}")
            
            st.divider()
            colA, colB = st.columns(2)
            with colA:
                st.subheader("Asset Contribution")
                if len(results[0].actual_contributions) > 1:
                    import altair as alt
                    pie_df = pd.DataFrame(list(results[0].actual_contributions.items()), columns=["Fund", "Current Value"])
                    fig = alt.Chart(pie_df).mark_arc(innerRadius=40).encode(
                        theta="Current Value",
                        color="Fund",
                        tooltip=["Fund", "Current Value"]
                    )
                    st.altair_chart(fig, width="stretch")
                else:
                    st.info("Single asset portfolio.")
            with colB:
                st.subheader("Metrics vs Benchmarks")
                st.metric("Portfolio 1Y Rolling Avg", format_perc(results[0].actual_1y_rolling))
                st.metric("Portfolio Max Drawdown", format_perc(results[0].actual_max_dd))
            
            st.divider()
            st.subheader("Comparative Overlay Chart")
            
            df_plot = pd.DataFrame(results[0].actual_timeline, columns=["Date", "Actual Portfolio"])
            df_plot.set_index("Date", inplace=True)
            
            for r in results:
                df_b = pd.DataFrame(r.benchmark_timeline, columns=["Date", r.benchmark.name])
                df_b.set_index("Date", inplace=True)
                df_plot = df_plot.join(df_b, how="outer")
            
            df_plot = df_plot.ffill().fillna(0.0)
            
            # Browser Crash Protection: 21 lines * 5000 daily points = locked SVG. Down-sample to Weekly!
            df_plot.index = pd.to_datetime(df_plot.index)
            df_plot = df_plot.resample('W-FRI').last().ffill()
            
            # Since line chart colors require passing a list of exact length, we dynamically create it.
            # Actual portfolio is blue, others are varying colors.
            if len(results) <= 6:
                color_list = ["#1f77b4"] + ["#2ca02c", "#ff7f0e", "#d62728", "#9467bd", "#8c564b", "#e377c2"][:len(results)]
                st.line_chart(df_plot, color=color_list)
            else:
                st.line_chart(df_plot)
            
        except Exception as e:
            st.error(f"Execution failed: {e}")
    
def page_portfolio_vs_portfolio():
    render_shell(
        "Heracles Duel Room",
        "Compare two portfolios against the same baseline and inspect which construction philosophy actually wins through time.",
    )
    st.title("Portfolio vs Portfolio")
    if len(st.session_state.portfolios) < 2:
        st.warning("Upload at least two portfolios to compare.")
        return
        
    col1, col2 = st.columns(2)
    with col1:
        p1_name = st.selectbox("Select Portfolio A", list(st.session_state.portfolios.keys()))
    with col2:
        other_ports = [k for k in st.session_state.portfolios.keys() if k != p1_name]
        p2_name = st.selectbox("Select Portfolio B", other_ports if other_ports else ["None"])
        
    benchmaps = {b.name: b for b in registry.get_benchmarks()}
    b_name = st.selectbox("Select Common Baseline Benchmark", list(benchmaps.keys()))
    
    if st.button("Battle Portfolios"):
        if p2_name == "None":
            st.error("Need a valid Portfolio B")
            return
            
        try:
            p1 = st.session_state.portfolios[p1_name]
            p2 = st.session_state.portfolios[p2_name]
            bench = benchmaps[b_name]
            
            res1 = uc_p2b.execute(p1, bench)
            res2 = uc_p2b.execute(p2, bench)
            
            colA, colB = st.columns(2)
            with colA:
                st.subheader(f"🛡️ {p1_name}")
                st.metric("Actual XIRR", format_perc(res1.actual_xirr))
                st.metric("Alpha vs Bench", format_perc(res1.alpha))
                st.metric("Final Value", format_curr(res1.actual_value))
                st.metric("Max Drawdown", format_perc(res1.actual_max_dd))
            with colB:
                st.subheader(f"⚔️ {p2_name}")
                st.metric("Actual XIRR", format_perc(res2.actual_xirr))
                st.metric("Alpha vs Bench", format_perc(res2.alpha))
                st.metric("Final Value", format_curr(res2.actual_value))
                st.metric("Max Drawdown", format_perc(res2.actual_max_dd))
                
            st.divider()
            st.subheader("Performance Race")
            
            df_1 = pd.DataFrame(res1.actual_timeline, columns=["Date", p1_name])
            df_2 = pd.DataFrame(res2.actual_timeline, columns=["Date", p2_name])
            df_1.set_index("Date", inplace=True)
            df_2.set_index("Date", inplace=True)
            
            df_plot = df_1.join(df_2, how="outer").ffill().fillna(0.0)
            st.line_chart(df_plot, color=["#1f77b4", "#d62728"]) # Blue and Red
            
        except Exception as e:
            st.error(f"Execution failed: {e}")

pg = st.navigation([
    st.Page(page_data_setup, title="1. Setup & Data", icon="🛠️"),
    st.Page(page_single_analysis, title="2. Single Analysis", icon="📈"),
    st.Page(page_portfolio_analysis, title="3. Portfolio Analysis", icon="📊"),
    st.Page(page_multi_benchmark, title="4. Multi-Benchmark", icon="🔀"),
    st.Page(page_portfolio_vs_portfolio, title="5. Port vs Port", icon="⚔️")
])

pg.run()
