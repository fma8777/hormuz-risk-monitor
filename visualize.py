import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sqlite3

# Load data from database
conn = sqlite3.connect("hormuz_macro.db")
df = pd.read_sql("SELECT * FROM macro_daily", conn, index_col="index", parse_dates=["index"])
conn.close()

# Key event timeline
key_events = {
    "2026-02-28": "US/Israel strike Iran",
    "2026-03-04": "Iran closes Hormuz",
    "2026-03-21": "Trump 48hr ultimatum",
    "2026-04-08": "Ceasefire agreed",
    "2026-04-13": "US naval blockade",
    "2026-04-17": "Iran reopens briefly",
    "2026-05-06": "Project Freedom pause",
    "2026-06-01": "Iran quits talks",
    "2026-06-09": "US resumes strikes",
    "2026-06-11": "Iran closes Hormuz again",
    "2026-06-12": "Peace deal text agreed",
}

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
fig.suptitle("Hormuz Risk Monitor: Shipping Crisis → Oil → Inflation Expectations",
             fontsize=14, fontweight="bold", y=0.98)

# Top panel: WTI oil price
ax1.plot(df.index, df["wti_price"], color="#c0392b", linewidth=1.8, label="WTI Crude")
ax1.set_ylabel("WTI ($/bbl)", fontsize=10)
ax1.fill_between(df.index, df["wti_price"], alpha=0.08, color="#c0392b")
ax1.legend(loc="upper left", fontsize=9)
ax1.grid(alpha=0.3)

# Middle panel: breakeven vs nominal yield
ax2.plot(df.index, df["breakeven_10y"], color="#e67e22", linewidth=1.8, label="10Y Breakeven Inflation")
ax2.plot(df.index, df["nominal_10y"],   color="#2980b9", linewidth=1.8, label="10Y Nominal Yield")
ax2.set_ylabel("Rate (%)", fontsize=10)
ax2.legend(loc="upper left", fontsize=9)
ax2.grid(alpha=0.3)

# Bottom panel: event timeline
event_dates = [pd.Timestamp(d) for d in key_events.keys()]
event_labels = list(key_events.values())
event_dates = [d for d in event_dates if df.index.min() <= d <= df.index.max()]

ax3.vlines(event_dates, 0, 1, color="#8e44ad", linewidth=2.5, alpha=0.8)
ax3.set_ylim(0, 2.0)
ax3.set_yticks([])
ax3.set_ylabel("Key Events", fontsize=10)
ax3.grid(alpha=0.2, axis="x")

for d, label in zip(event_dates, list(key_events.values())):
    if df.index.min() <= d <= df.index.max():
        ax3.annotate(label, xy=(d, 1.05), fontsize=7.5, color="#4a235a",
                    rotation=90, ha="center", va="bottom")

# Add vertical dashed lines across all panels
for d in event_dates:
    for ax in [ax1, ax2]:
        ax.axvline(d, color="#aaa", linestyle="--", linewidth=0.8, alpha=0.6)

ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("hormuz_monitor.png", dpi=150, bbox_inches="tight")
print("Chart saved as hormuz_monitor.png")
