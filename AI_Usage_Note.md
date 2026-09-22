# AI Usage Note
**Author:** Adarsh Kasaundhan

### Tools Used
*   Gemini (LLM for brainstorming experimental design and statistical falsification)
*   Cursor / Antigravity IDE (Vibe Coding and rapid generation of Python and Pandas boilerplate)

### How I Used Them
I utilized AI primarily as a high-speed typist to scaffold the data pipeline and execute standard statistical methods (`scipy.stats`). Leveraging Vibe Coding methodologies, I prompted the AI to generate the `yfinance` data retrieval block, the vectorization logic for calculating forward returns, and the DataFrame validation checks. 

### My Own Decisions & Logic Overrides
My background in competitive programming heavily influenced how I managed state and edge cases, which AI tools frequently mishandle. 
*   **Overlap Handling:** When filtering events, the AI initially struggled to account for overlapping trades. I implemented strict state management logic to ensure that if a new -2.0% drop triggered while a T+5 holding period was already active, the signal was entirely ignored. This guaranteed statistical independence for every observation.
*   **Falsification over Optimization:** The robustness matrix revealed that tweaking the threshold to -2.5% generated a positive return. The AI suggested modifying the core hypothesis to reflect this better outcome. I explicitly rejected this suggestion. Selecting the best threshold post-hoc is data snooping. I made the executive decision to reject the hypothesis entirely rather than curve-fit a backtest.

### Incorrect Suggestions & Disagreements
*   **Look-Ahead Bias:** The AI initially suggested entering the trade at the Close of Day T. I disagreed and rewrote the execution logic to enter at the Open of Day T+1. Entering on the close of a day where a -2.0% drop is actively happening introduces severe look-ahead bias, as the official closing price is not actionable.
*   **Frictionless Vacuum:** Early AI code snippets ignored transaction costs. I manually enforced a 20 basis point round-trip friction cost to ensure the statistical mean was grounded in market realities.

### What I Learned
AI is exceptional at setting up data pipelines and calculating baseline statistical arrays. However, it operates in a frictionless vacuum. It will happily optimize a backtest into a 90% win rate by ignoring transaction costs, execution mechanics (like slippage on the open), and look-ahead bias. The exercise reinforced that while AI can rapidly build the computational engine, the quantitative researcher must dictate the physical laws of the simulation.
