# Labelled historical episode benchmark

This benchmark divides the fixed EUR/USD M1 research fixture into 20 chronological episodes and compares the intelligence engine with a **separate, transparent OHLC reference annotator**.

## Labels
The reference annotator checks the terminal portion of each episode for liquidity sweep, displacement, CHoCH/BOS-style structural break, and FVG.

The engine under test is not used to create these labels.

## Status
These are **reference benchmark labels, not human ground truth**. They support repeatable engineering evaluation but must not be presented as validated market-structure truth or predictive performance.

## Evaluation
- Event detection: aggregate precision, recall, F1.
- Sequence: preservation of reference relative event ordering where matched pairs exist.
- Analogue: each later episode is compared only with earlier episodes; outcome statistics are descriptive.
- Chronology is preserved and no future observations are used to construct an episode label.

## Interpretation
Scores measure agreement with explicit reference rules. They do not establish trading edge, profitability, causality, or live readiness.
