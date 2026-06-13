import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings("ignore")
import numpy as np
from statsmodels.tsa.api import VAR

# Load data
conn = sqlite3.connect("hormuz_macro.db")
macro = pd.read_sql("SELECT * FROM macro_daily", conn, index_col="index", parse_dates=["index"])
bdti  = pd.read_sql("SELECT * FROM bdti", conn, index_col="date", parse_dates=["date"])
conn.close()

# Merge
df = macro.join(bdti, how="inner").dropna()

# Raw daily changes
df["bwet_chg"]      = df["bdti"].diff()
df["wti_chg"]       = df["wti_price"].diff()
df["breakeven_chg"] = df["breakeven_10y"].diff()

# Log returns
df["bwet_log"]      = np.log(df["bdti"]).diff()
df["wti_log"]       = np.log(df["wti_price"]).diff()
df["breakeven_log"] = np.log(df["breakeven_10y"]).diff()

data_raw = pd.DataFrame({
    "bwet_chg":      df["bwet_chg"],
    "wti_chg":       df["wti_chg"],
    "breakeven_chg": df["breakeven_chg"],
}).dropna()

data_log = pd.DataFrame({
    "bwet_log": df["bwet_log"],
    "wti_log":  df["wti_log"],
    "breakeven_log": df["breakeven_log"],
}).dropna()

def run_var_forecast(data, label, col_idx=2, is_log=False):
    model = VAR(data)
    results = model.fit(2)
    lag_order = 2
    forecast_input = data.values[-lag_order:]
    forecast = results.forecast_interval(y=forecast_input, steps=10, alpha=0.2)
    fc_mean, fc_lower, fc_upper = forecast

    last_date = df.index[-1]
    forecast_dates = pd.bdate_range(start=last_date, periods=11)[1:]
    fc_df = pd.DataFrame({
        "fc":    fc_mean[:, col_idx],
        "lower": fc_lower[:, col_idx],
        "upper": fc_upper[:, col_idx],
    }, index=forecast_dates)

    last_val = df["breakeven_10y"].iloc[-1]
    if is_log:
        # Convert log return forecasts back to levels
        fc_df["breakeven_forecast"] = last_val * np.exp(fc_df["fc"].cumsum())
        fc_df["lower_level"]        = last_val * np.exp(fc_df["lower"].cumsum())
        fc_df["upper_level"]        = last_val * np.exp(fc_df["upper"].cumsum())
    else:
        fc_df["breakeven_forecast"] = last_val + fc_df["fc"].cumsum()
        fc_df["lower_level"]        = last_val + fc_df["lower"].cumsum()
        fc_df["upper_level"]        = last_val + fc_df["upper"].cumsum()

    print(f"\n=== 10-Day Breakeven Forecast ({label}) ===")
    print(fc_df[["breakeven_forecast", "lower_level", "upper_level"]].round(4))

    # Plot
    fig, ax = plt.subplots(figsize=(13, 5))
    hist = df["breakeven_10y"].iloc[-60:]
    ax.plot(hist.index, hist, color="#e67e22", linewidth=1.8, label="Historical 10Y Breakeven")
    ax.plot(fc_df.index, fc_df["breakeven_forecast"],
            color="#2980b9", linewidth=2, linestyle="--", label=f"VAR Forecast ({label})")
    ax.fill_between(fc_df.index, fc_df["lower_level"], fc_df["upper_level"],
                    alpha=0.2, color="#2980b9", label="80% Confidence Interval")
    ax.axvline(last_date, color="gray", linestyle=":", linewidth=1.2, label="Forecast start")
    ax.set_ylabel("10Y Breakeven Inflation (%)", fontsize=10)
    ax.set_title(f"VAR Forecast: 10Y Breakeven — Next 10 Trading Days ({label})\n"
                 "Inputs: BWET (tanker ETF), WTI crude, 10Y breakeven", fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    fname = f"forecast_{label.lower().replace(' ', '_')}.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    print(f"Chart saved as {fname}")
    plt.close()

run_var_forecast(data_raw, "raw daily change", col_idx=2, is_log=False)
run_var_forecast(data_log, "log return",       col_idx=2, is_log=True)