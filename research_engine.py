import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
import warnings

# Suppress yfinance future warnings for cleaner terminal output in the video
warnings.simplefilter(action='ignore', category=FutureWarning)

# ==========================================
# 1. CONFIGURATION 
# Engine is configurable without rewriting logic
# ==========================================
TICKER = "^NSEI"
START_DATE = "2010-01-01"
END_DATE = "2026-08-31"
SPLIT_DATE = "2022-01-01"  # Data after this date is strictly Out-of-Sample
THRESHOLD = -0.02          # -2.0% drop
HOLDING_PERIOD = 5         # 5 trading days
TRANSACTION_COST = 0.002   # 20 bps total round-trip

# ==========================================
# 2. DATA VALIDATION
# ==========================================
def load_and_validate_data(ticker, start, end):
    print(f"Sourcing NIFTY data ({ticker}) from {start} to {end}...")
    # auto_adjust=False suppresses a common yfinance warning
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df[['Open', 'High', 'Low', 'Close']].dropna()
    
    print("\n--- Data Validation ---")
    if df.index.has_duplicates:
        print("[-] Duplicate dates found. Dropping.")
        df = df[~df.index.duplicated(keep='first')]
    else:
        print("[+] No duplicate dates.")
        
    if not df.index.is_monotonic_increasing:
        print("[-] Incorrect ordering found. Sorting.")
        df = df.sort_index()
    else:
        print("[+] Dates are correctly ordered.")
        
    invalid_ohlc = df[df['Low'] > df['High']]
    if not invalid_ohlc.empty:
        print(f"[-] Found {len(invalid_ohlc)} invalid OHLC rows. Dropping.")
        df = df.drop(invalid_ohlc.index)
    else:
        print("[+] OHLC values are logically valid (Low <= High).")
        
    print(f"[+] Total trading days available: {len(df)}")
    return df

# ==========================================
# 3. EVENT DETECTION & OVERLAP HANDLING
# ==========================================
def detect_events(df, threshold, holding_period, t_cost):
    df['Daily_Return'] = df['Close'].pct_change()
    
    df['Entry_Price'] = df['Open'].shift(-1)
    df['Exit_Price'] = df['Close'].shift(-holding_period)
    
    df['Forward_Return_Gross'] = (df['Exit_Price'] - df['Entry_Price']) / df['Entry_Price']
    df['Forward_Return_Net'] = df['Forward_Return_Gross'] - t_cost
    
    events = df[df['Daily_Return'] <= threshold].copy()
    events = events.dropna(subset=['Forward_Return_Net'])
    
    active_until = pd.Timestamp('1900-01-01')
    independent_events = []
    
    for event_date, row in events.iterrows():
        if event_date > active_until:
            independent_events.append(row)
            current_loc = df.index.get_loc(event_date)
            exit_loc = current_loc + holding_period
            if exit_loc < len(df):
                active_until = df.index[exit_loc]
            else:
                active_until = df.index[-1]
                
    return pd.DataFrame(independent_events)

# ==========================================
# 4. STATISTICAL ANALYSIS
# ==========================================
def calculate_statistics(events, phase_name):
    print(f"\n--- Event Statistics ({phase_name}) ---")
    n_obs = len(events)
    print(f"Number of Independent Observations: {n_obs}")
    
    if n_obs == 0:
        return
        
    returns = events['Forward_Return_Net']
    mean_ret = returns.mean() * 100
    median_ret = returns.median() * 100
    win_rate = (returns > 0).mean() * 100
    volatility = returns.std() * 100
    
    print(f"Mean Net Return:   {mean_ret:.2f}%")
    print(f"Median Net Return: {median_ret:.2f}%")
    print(f"Win Rate:          {win_rate:.2f}%")
    print(f"Volatility (Std):  {volatility:.2f}%")

# ==========================================
# 5. STATISTICAL EVIDENCE & BASELINE
# ==========================================
def evaluate_statistical_evidence(df, events, holding_period):
    print("\n--- Statistical Evidence & Baseline ---")
    df['Baseline_Forward_Net'] = (df['Close'].shift(-holding_period) - df['Open'].shift(-1)) / df['Open'].shift(-1) - TRANSACTION_COST
    baseline_returns = df['Baseline_Forward_Net'].dropna()
    event_returns = events['Forward_Return_Net']
    
    baseline_mean = baseline_returns.mean() * 100
    event_mean = event_returns.mean() * 100
    
    print(f"Unconditional Baseline Mean Return: {baseline_mean:.2f}%")
    print(f"Event-Driven Mean Return:           {event_mean:.2f}%")
    
    t_stat, p_value = stats.ttest_1samp(event_returns, baseline_returns.mean())
    print(f"T-Statistic: {t_stat:.2f}")
    print(f"P-Value:     {p_value:.4f}")
    
    if p_value < 0.05:
        print("[+] Evidence suggests the event returns are statistically significant compared to the baseline.")
    else:
        print("[-] Evidence is NOT statistically significant. The returns could be random noise.")

# ==========================================
# 6. ROBUSTNESS & PARAMETER SENSITIVITY
# ==========================================
def run_robustness_checks(df):
    print("\n--- Robustness Checks (In-Sample Data) ---")
    thresholds_to_test = [-0.015, -0.020, -0.025]
    holding_periods_to_test = [3, 5, 7]
    
    results = []
    for t in thresholds_to_test:
        for hp in holding_periods_to_test:
            test_events = detect_events(df.copy(), t, hp, TRANSACTION_COST)
            if not test_events.empty:
                mean_ret = test_events['Forward_Return_Net'].mean() * 100
                win_rate = (test_events['Forward_Return_Net'] > 0).mean() * 100
                results.append((t, hp, len(test_events), mean_ret, win_rate))
                
    robustness_df = pd.DataFrame(results, columns=['Threshold', 'Holding_Period', 'Trades', 'Mean_Net_Return(%)', 'Win_Rate(%)'])
    print(robustness_df.to_string(index=False))

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Fetch Data
    nifty_df = load_and_validate_data(TICKER, START_DATE, END_DATE)
    
    # Train/Test Split for Out-of-Sample Validation
    # The .copy() ensures we don't get SettingWithCopy warnings
    train_df = nifty_df[:SPLIT_DATE].copy()
    test_df = nifty_df[SPLIT_DATE:].copy()
    print(f"\nData split into Research (until {SPLIT_DATE}) and Out-of-Sample (after {SPLIT_DATE}).")
    
    # IN-SAMPLE (Research Phase)
    valid_events_train = detect_events(train_df, THRESHOLD, HOLDING_PERIOD, TRANSACTION_COST)
    calculate_statistics(valid_events_train, "IN-SAMPLE")
    evaluate_statistical_evidence(train_df, valid_events_train, HOLDING_PERIOD)
    run_robustness_checks(train_df)
    
    # OUT-OF-SAMPLE (Testing Phase)
    valid_events_test = detect_events(test_df, THRESHOLD, HOLDING_PERIOD, TRANSACTION_COST)
    calculate_statistics(valid_events_test, "OUT-OF-SAMPLE")