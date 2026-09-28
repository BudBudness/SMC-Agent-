# Real EURUSD research run

## Source
Public EUR/USD M1 CSV fixture:
https://github.com/danielfcastro/MLRobotForex/blob/dev/EURUSD/EURUSD1.csv

The upstream dataset is described as EUR/USD 1-minute historical data. The repository documents the original HistData-style structure and timezone convention. The SMC Agent adapter accepts this compatible CSV schema.

## Validation
- Rows: 65,007
- Start: 2019-09-10 04:10 UTC
- End: 2019-11-13 00:34 UTC
- OHLC validation: PASS
- Timestamp normalization: PASS
- Pipeline execution: PASS
- Benchmark contract: PASS

## Intelligence snapshot
- Weekly: NEUTRAL
- Daily: LONG
- 4H: SHORT
- 15M: SHORT
- 1M: LONG
- Cross-timeframe conflicts detected: 3
- FVGs detected in source history: 898
- Order blocks detected in source history: 976
- Final report conclusion: structural conflict remained unresolved.

## Historical reaction benchmark
Observed events from the final intelligence snapshot: 3.

Forward close reaction summary:
- 1 M1: mean +0.00361%, positive rate 50%
- 3 M1: mean +0.00362%, positive rate 100%
- 5 M1: mean -0.00135%, positive rate 50%
- 10 M1: mean +0.00046%, positive rate 50%
- 20 M1: mean +0.01356%, positive rate 100%

These figures are descriptive observations from three events, not statistical evidence of predictive performance.

## Remaining research work
A larger labelled historical episode set is still required before claiming detection accuracy, sequence accuracy, or generalization.
