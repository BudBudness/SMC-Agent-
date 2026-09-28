# SMC Agent

Macro-to-Micro Smart Money Concepts research and paper-trading engine.

## Operating hierarchy
12M regime → 6M context → 3M macro → Weekly thesis → Daily target → 4H delivery → 1H liquidity → 15M confirmation → 5M refinement → 1M fill.

**Weekly structure is authoritative. Lower timeframes cannot override a contradictory Weekly thesis.**

## Modes
- BACKTEST: causal replay with spread/slippage/commission model.
- PAPER: simulated orders and audit ledger.
- LIVE: blocked by default and requires explicit deployment configuration plus a final safety review.

## Risk defaults
0.5% trade risk · 1.5% daily loss limit · 3% weekly loss limit · 1 simultaneous position · 1 correlated directional exposure · no martingale.

## Validation
Run pytest. Historical data must be causal; fills use only confirmed bars and conservative same-bar stop handling. Walk-forward/OOS evaluation is required before any profitability claim.

## Data
download_dukascopy.py provides the EUR/USD tick-archive ingestion path; build_bars.py converts normalized ticks to 1m/5m/15m/1h/4h/D/W/3M/6M/12M bars. Validate the resulting files before research.

## Dashboard
streamlit run dashboard/app.py

This repository is a research baseline. It does not claim profitability or production live-trading readiness.
