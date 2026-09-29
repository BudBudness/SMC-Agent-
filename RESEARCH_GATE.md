# Research Gate

## Gate 1 — Code
- [x] Execution architecture removed
- [x] Canonical intelligence pipeline
- [x] Stable report schema
- [x] Dataset validator
- [x] Benchmark contract
- [x] CI workflow

## Gate 2 — Verification
- [x] GitHub Actions research runs completed successfully
- [x] Full test suite passes
- [x] No stale execution tests/scripts remain

Verified on commit `d1c8d309e7cc23c536e39c33f7e6ff96f1f5d492`:
- SMC intelligence validation #136 — PASS
- Long-history MTF reconstruction #13 — PASS
- Real EUR/USD validation #15 — PASS on the preceding swing-edge correction
- Stale `scripts/paper_loop.py` removed before the final validation chain

## Gate 3 — Data
- [x] Real EUR/USD dataset loaded
- [x] OHLC/timezone/gap validation completed
- [x] Multi-timeframe alignment validated in pipeline contract
- [x] Long-history dataset published as a versioned research release

Long-history dataset:
- Source: HistData EUR/USD M1
- Rows: 8,307,639
- Start: 2003-05-01 00:00 UTC
- End: 2026-09-24 19:58 UTC
- Release tag: `research-data`
- Assets: normalized M1 dataset, MTF coverage, substantive MTF evaluation

MTF coverage:
- 12M: 25
- 6M: 48
- 3M: 95
- W: 1,222
- D: 7,309
- 4H: 37,607
- 1H: 144,719
- 15M: 577,495
- 5M: 1,726,982
- 1M: 8,307,639

## Gate 4 — Benchmark
- [x] Multi-episode reference-labelled benchmark added (20 chronological episodes)
- [x] Event detection benchmark scored by independent reference rules
- [x] Sequence benchmark scored
- [x] Analogue benchmark scored descriptively
- [x] Long-history substantive MTF evaluation completed

## Gate 5 — Research reproducibility
- [x] Fixed dataset/version
- [x] Fixed configuration/code revision
- [x] Reproducible report artifact
- [x] Look-ahead checks
- [x] Out-of-sample separation

The labelled benchmark uses rule-based reference labels, not human ground truth. Independent-source cross-validation and human annotation remain research-quality upgrades. No predictive, profitability, or live-readiness claim is implied.
