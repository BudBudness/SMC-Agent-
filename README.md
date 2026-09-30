# Henryz SMC Intelligence — Market Investigation & Intelligence System

Henryz SMC Intelligence is an investigation and intelligence system for reconstructing market structure, liquidity, Smart Money Concepts events, macro context, historical analogues, competing hypotheses, and evidence.

## Core pipeline

**DATA → NORMALIZATION → MULTI-TIMEFRAME STATE → STRUCTURE → LIQUIDITY → SMC EVENTS → MACRO CONTEXT → HISTORICAL ANALOGUES → HYPOTHESES → EVIDENCE + CONTRADICTIONS → INVALIDATION CONDITIONS → INTELLIGENCE REPORT**

## Investigation hierarchy

12M regime → 6M context → 3M macro structure → Weekly direction → Daily context → 4H delivery/AMD → 1H liquidity → 15M structure → 5M refinement → 1M precision context.

Weekly structure is authoritative. Lower timeframes are retained as evidence and can be reported as contradictions rather than silently overriding higher-timeframe structure.

## Intelligence capabilities

1. Cross-timeframe agreement and contradiction analysis.
2. Ordered event sequencing for liquidity, inducement, sweep, rejection, displacement, CHoCH/BOS, FVG/OB and subsequent reaction.
3. Inducement investigation requiring internal-liquidity and structural context.
4. Similarity-based historical analogue matching and conditional statistics.
5. Macro surprise classification and macro-to-price reaction context.
6. Fixed-horizon historical event studies.
7. Evidence ledger linking observations to claims, methods, contradictions and invalidation.
8. Evidence-based intelligence reports with competing hypotheses.
9. OHLC/timeframe dataset integrity validation and research tests.

## Dashboard data architecture

The live dashboard separates full-history structural intelligence from recent microstructure detail. The validated 2003→latest EUR/USD M1 history is reconstructed into all ten analysis timeframes in CI. A compact release artifact stores each timeframe's full-history state and bounded OHLC visualization tail, while the dashboard M1 window remains lightweight. This prevents partial 12M/6M/3M reconstruction from a 90-day slice.

The dashboard does not treat heuristic detector counts as predictive accuracy, and hypothesis outputs are presented as competing research hypotheses rather than ranked recommendations.

## Output

The system reports:

- market state
- timeframe structure
- liquidity map
- detected events and their sequence
- macro context
- historical analogues
- competing hypotheses
- supporting evidence
- contradictions
- invalidation conditions
- unresolved questions

A scenario is an investigation artifact, not an order or recommendation.

## Explicitly excluded

- live trading
- paper trading
- order placement
- broker adapters
- position management
- automated execution

## Research integrity

Historical analysis must avoid lookahead. Confirmed candles are required for structural conclusions. In-sample evidence must be separated from out-of-sample evidence. Historical frequency is descriptive and is not treated as a prediction.

No profitability claim is made without adequate out-of-sample evidence.
