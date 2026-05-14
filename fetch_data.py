from dotenv import load_dotenv
import os
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

import pandas as pd
import yfinance as yf
from fredapi import Fred

fred = Fred(api_key=FRED_API_KEY)

START = "2026-01-01"
END   = "2026-05-11"

def fetch_fred_series():
    """Fetch three FRED series: 10Y nominal yield, 10Y TIPS real yield, 10Y breakeven inflation."""
    nominal   = fred.get_series("DGS10",   START, END)
    real      = fred.get_series("DFII10",  START, END)
    breakeven = fred.get_series("T10YIE",  START, END)

    df = pd.DataFrame({
        "nominal_10y":   nominal,
        "real_10y":      real,
        "breakeven_10y": breakeven,
    })
    return df

def fetch_oil_price():
    """Fetch daily WTI crude oil futures closing prices from Yahoo Finance."""
    wti = yf.download("CL=F", start=START, end=END, auto_adjust=True)
    wti.columns = wti.columns.get_level_values(0)  # Flatten MultiIndex columns returned by yfinance
    wti = wti[["Close"]].rename(columns={"Close": "wti_price"})
    return wti

def merge_and_clean(df_rates, df_oil):
    """Merge rates and oil price data, keeping only dates present in both series."""
    df = df_rates.join(df_oil, how="inner")
    df = df.dropna()

    # Calculate daily changes
    df["wti_chg"]       = df["wti_price"].diff()
    df["breakeven_chg"] = df["breakeven_10y"].diff()
    df["nominal_chg"]   = df["nominal_10y"].diff()

    return df

import sqlite3

def save_to_db(df, db_path="hormuz_macro.db"):
    """Save merged DataFrame to SQLite database."""
    conn = sqlite3.connect(db_path)
    df.to_sql("macro_daily", conn, if_exists="replace", index=True)
    conn.close()
    print(f"Saved {len(df)} rows to {db_path}.")

if __name__ == "__main__":
    df_rates = fetch_fred_series()
    df_oil   = fetch_oil_price()
    df       = merge_and_clean(df_rates, df_oil)
    save_to_db(df)

    print(df.tail(10))
    print(f"\nTotal: {len(df)} trading days loaded.")