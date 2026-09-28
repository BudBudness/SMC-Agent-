# Henry SMC specification audit

## Implemented baseline
- 12M/6M/3M/Weekly/Daily/4H/1H/15M/5M/1M hierarchy.
- Weekly structure authority and neutral/no-trade path.
- Liquidity mapping and sweep detection.
- CHoCH/BOS structure confirmation.
- Displacement classification.
- FVG and Order Block detection.
- Premium/discount location.
- 4H AMD classification hook.
- News-lock interface.
- A/A+ threshold and explicit NO TRADE output.
- 0.5% trade risk, daily/weekly loss limits, position limits.
- Causal backtest, spread/slippage/commission model.
- Walk-forward/OOS modules.
- Paper broker, paper loop, audit log.
- MT5/OANDA live adapter boundaries with live disabled by default.
- Streamlit research dashboard.
- CI workflow and regression tests.

## Still required before any live-trading claim
- Real broker/data-provider integration tests in a controlled environment.
- Full inducement definition based on internal/external structure rather than the conservative baseline heuristic.
- Protected-swing and equal-high/equal-low clustering validation across instruments.
- Full T1/T2 partial-exit lifecycle and position management.
- Economic-calendar provider with actual/expected/previous fields and event classification.
- Full session model and volatility/spread gates.
- Real historical EUR/USD dataset validation and multi-timeframe continuity checks.
- True walk-forward parameter fitting where model parameters are learned only from train windows.
- OOS statistical robustness checks and sensitivity analysis.
- Deployment-specific kill switch, emergency-close verification, API failure tests, and operational monitoring.

**Policy:** no profitability claim and no live execution until these controls are verified with real data and a separate deployment review.
