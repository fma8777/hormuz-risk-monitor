import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load data
conn = sqlite3.connect("hormuz_macro.db")
macro = pd.read_sql("SELECT * FROM macro_daily", conn, index_col="index", parse_dates=["index"])
bdti  = pd.read_sql("SELECT * FROM bdti", conn, index_col="date", parse_dates=["date"])
conn.close()

# Merge
df = macro.join(bdti, how="inner").dropna()
df["bdti_chg"]      = df["bdti"].diff(5)
df["breakeven_chg"] = df["breakeven_10y"].diff(5)

# ── Lead-lag analysis ──────────────────────────────────────────
print("Lead-lag: BWET 5-day change vs future breakeven 5-day change\n")
results = []
for lag in [0, 1, 2, 3, 5, 10, 15, 20]:
    r = df["bdti_chg"].corr(df["breakeven_chg"].shift(-lag))
    r2 = r ** 2
    results.append((lag, round(r, 3)))
    print(f"  BWET today vs breakeven +{lag}d: r = {r:.3f}  |  R² = {r2:.3f}  ({r2*100:.1f}% variance explained)")

best_lag = max(results, key=lambda x: abs(x[1]))
print(f"\nStrongest signal: lag = {best_lag[0]} days (r = {best_lag[1]})")

# ── Plot: BWET vs WTI vs Breakeven ────────────────────────────
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
fig.suptitle("Shipping Stress → Oil → Inflation: BWET as Leading Indicator",
             fontsize=13, fontweight="bold", y=0.98)

ax1.plot(df.index, df["bdti"], color="#8e44ad", linewidth=1.8, label="BWET (tanker ETF)")
ax1.set_ylabel("BWET ($/share)", fontsize=10)
ax1.legend(loc="upper left", fontsize=9)
ax1.grid(alpha=0.3)

ax2.plot(df.index, df["wti_price"], color="#c0392b", linewidth=1.8, label="WTI Crude")
ax2.set_ylabel("WTI ($/bbl)", fontsize=10)
ax2.legend(loc="upper left", fontsize=9)
ax2.grid(alpha=0.3)

ax3.plot(df.index, df["breakeven_10y"], color="#e67e22", linewidth=1.8, label="10Y Breakeven")
ax3.set_ylabel("Breakeven (%)", fontsize=10)
ax3.legend(loc="upper left", fontsize=9)
ax3.grid(alpha=0.3)

for ax in [ax1, ax2, ax3]:
    ax.axvline(pd.Timestamp("2026-03-04"), color="#aaa", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.axvline(pd.Timestamp("2026-04-13"), color="#aaa", linestyle="--", linewidth=0.8, alpha=0.7)

ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("lead_lag.png", dpi=150, bbox_inches="tight")
print("\nChart saved as lead_lag.png")