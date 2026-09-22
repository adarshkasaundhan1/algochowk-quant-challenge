# algochowk-quant-challenge

# NIFTY 50 Event-Driven Mean Reversion Backtest

**[Link to 2-3 minute Video Walkthrough]** *(Insert your YouTube/Drive link here)*

## Overview
This repository contains a Python-based quantitative research engine designed to investigate the hypothesis that the NIFTY 50 index exhibits a measurable, mean-reverting recovery following a significant one-day drop. 

**Author:** Adarsh Kasaundhan

## Setup & Execution
1. Ensure Python 3.9+ is installed.
2. Install the required dependencies:
   ```bash
   pip install pandas numpy yfinance scipy

  ## Methodology
   The experiment is structured to prioritize statistical rigor over curve-fitting maximum returns.Event Definition: A "significant fall" is quantified as a daily close-to-close return of $\le -2.0\%$.Recovery / Holding Period: The recovery is measured as the net forward return over the subsequent 5 trading days.Execution: To strictly eliminate look-ahead bias, trades are assumed to execute at the Open price of Day T+1.State Management (Overlap Handling): To ensure statistical independence across observations, overlapping events are filtered out. If a new -2.0% drop occurs while a T+5 holding period is already active, the new signal is ignored until the current timeline resolves.Evaluation: A 1-sample t-test is applied to compare the event-driven mean returns against the unconditional normal NIFTY forward returns over the same period.

  ## Assumptions
Friction: A total transaction cost of 20 basis points (0.20%) is deducted per round-trip trade to account for retail brokerage, tax, and slippage.

Liquidity: The model assumes sufficient liquidity at the market open on Day T+1 to fill orders without triggering catastrophic market impact.

Statistical Evidence & Baseline Results
The empirical evidence strictly rejects the hypothesis. During the In-Sample period (2010-2021), the strategy generated a mean net return of -0.34% across 65 independent observations, which underperformed the unconditional baseline NIFTY return of -0.09%.

Furthermore, the 1-sample t-test yielded a p-value of 0.5666. Because the p-value is significantly higher than the 0.05 alpha threshold, we fail to reject the null hypothesis. Any deviations from the baseline are statistically indistinguishable from random market noise.

## Robustness & Overfitting Analysis
The robustness matrix revealed that altering the threshold to -2.5% improved the historical win rate to 66.6% with a positive mean return. However, adopting this threshold after observing the data is a textbook example of post-hoc parameter selection and data snooping. The fragility of the returns across the -1.5% and -2.0% bands indicates that the underlying market microstructure does not reliably support mean-reversion on a 5-day horizon.

## Out-of-Sample (OOS) Validation & Limitations
In the Out-of-Sample period (2022-2026), the strategy yielded a positive mean net return of 0.62% across 15 events. However, critical analysis invalidates this as a tradable edge. The median net return was -0.21%, and the win rate was only 46.67%. This massive divergence between the mean and median proves the positive expected value was skewed by extreme outliers, not consistent recovery mechanics.

When accounting for transaction costs and strictly eliminating overlapping events, buying a -2.0% dip in the NIFTY 50 index does not yield a statistically significant, mean-reverting edge over a 5-day holding period. The evidence does not deserve to be believed or traded.
