import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sqlite3

# Load data
conn = sqlite3.connect("hormuz_macro.db")
df = pd.read_sql("SELECT * FROM macro_daily", conn, index_col="index", parse_dates=["index"])
conn.close()

# Static correlation (before/after blockade)
pre  = df[df.index < "2026-04-13"]
post = df[df.index >= "2026-04-13"]

def show_corr(label, data):
    r = data["wti_chg"].corr(data["breakeven_chg"])
    print(f"{label}: oil vs breakeven correlation = {r:.3f}  (n={len(data)} days)")

show_corr("Pre-blockade  (Jan–Apr 12)", pre)
show_corr("Post-blockade (Apr 13–now)", post)

# Rolling 30-day correlation
df["rolling_corr"] = (
    df["wti_chg"]
    .rolling(window=30)
    .corr(df["breakeven_chg"])
)

# Save rolling correlation to database
conn = sqlite3.connect("hormuz_macro.db")
df[["rolling_corr"]].to_sql("rolling_correlation", conn, if_exists="replace", index=True)
conn.close()
print("Rolling correlation saved to database.")

# Plot
fig, ax = plt.subplots(figsize=(13, 4))
ax.plot(df.index, df["rolling_corr"], color="#2980b9", linewidth=1.8, label="30-day rolling correlation (oil vs breakeven)")
ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
ax.axvline(pd.Timestamp("2026-03-04"), color="#c0392b", linewidth=1, linestyle="--", alpha=0.7, label="Iran closes Hormuz")
ax.axvline(pd.Timestamp("2026-04-13"), color="#8e44ad", linewidth=1, linestyle="--", alpha=0.7, label="US naval blockade")
ax.set_ylabel("Correlation (r)", fontsize=10)
ax.set_title("30-Day Rolling Correlation: WTI Oil Price Change vs 10Y Breakeven Change", fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("rolling_correlation.png", dpi=150)
print("Chart saved as rolling_correlation.png")