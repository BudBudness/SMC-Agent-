# SMC Agent

Macro-to-Micro Smart Money Concepts research engine.

## Hierarchy
12M regime -> 6M context -> 3M macro -> Weekly thesis -> Daily target -> 4H delivery -> 1H liquidity -> 15M confirmation -> 5M refinement -> 1M fill.

Weekly structure is authoritative. Lower timeframes cannot override a contradictory Weekly thesis.

## Safety
- BACKTEST / PAPER by default
- LIVE execution disabled unless explicitly enabled
- 0.5% default risk/trade
- 1.5% daily loss limit
- 3% weekly loss limit
- one simultaneous trade
- no martingale
- stale data, spread, volatility, API and news locks are no-trade conditions
- A/A+ only are execution eligible

## Install
```bash
pip install -e ".[test]"
pytest
```

## Run
```bash
python -m smc_agent.main data.csv
```

This repository is a research baseline. Profitability is not claimed without causal out-of-sample validation.
