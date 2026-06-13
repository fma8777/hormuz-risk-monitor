from dotenv import load_dotenv
import os
import pandas as pd
import sqlite3
import yfinance as yf

def fetch_bdti(start="2026-01-01"):
    """Fetch shipping proxy via Breakwave Tanker & Shipping ETF (BWET)."""
    df = yf.download("BWET", start=start, auto_adjust=True)
    df.columns = df.columns.get_level_values(0)
    df = df[["Close"]].rename(columns={"Close": "bdti"})
    df.index.name = "date"
    df = df.dropna()
    return df

def save_bdti_to_db(df, db_path="hormuz_macro.db"):
    """Save BDTI data to SQLite database."""
    conn = sqlite3.connect(db_path)
    df.to_sql("bdti", conn, if_exists="replace", index=True)
    conn.close()
    print(f"Saved {len(df)} rows of BDTI data.")

if __name__ == "__main__":
    df = fetch_bdti()
    print(df.tail(10))
    save_bdti_to_db(df)