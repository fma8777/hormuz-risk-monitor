import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings("ignore")
from statsmodels.tsa.api import VAR

# Load data
conn = sqlite3.connect("hormuz_macro.db")
macro = pd.read_sql("SELECT * FROM macro_daily", conn, index_col="index", parse_dates=["index"])
bdti  = pd.read_sql("SELECT * FROM bdti", conn, index_col="date", parse_dates=["date"])
conn.close()

# Merge and compute log returns
df = macro.join(bdti, how="inner").dropna()
data = pd.DataFrame({
    "bwet_log":      np.log(df["bdti"]).diff(),
    "wti_log":       np.log(df["wti_price"]).diff(),
    "breakeven_log": np.log(df["breakeven_10y"]).diff(),
}).dropna()

# ── Fit VAR ───────────────────────────────────────────────────
model = VAR(data)
results = model.fit(2)

# ── Impulse Response Function ─────────────────────────────────
irf = results.irf(periods=10)

# Extract BWET shock → breakeven response
# irf.irfs shape: (periods+1, n_vars, n_vars)
# [period, response_var, impulse_var]
# bwet=0, wti=1, breakeven=2
bwet_to_breakeven = irf.irfs[:, 2, 0]   # breakeven response to BWET shock
lower = irf.irfs[:, 2, 0] - 1.28 * irf.stderr()[:, 2, 0]
upper = irf.irfs[:, 2, 0] + 1.28 * irf.stderr()[:, 2, 0]

periods = np.arange(len(bwet_to_breakeven))

# Convert log response to approximate bp move
# breakeven is ~2.3%, so 1% log move ≈ 2.3bp
last_breakeven = df["breakeven_10y"].iloc[-1]
scale = last_breakeven * 100  # convert to bp
bwet_bp = bwet_to_breakeven * scale
lower_bp = lower * scale
upper_bp = upper * scale

print("=== IRF: BWET 1-SD Shock → 10Y Breakeven Response (bp) ===")
for i, (b, lo, hi) in enumerate(zip(bwet_bp, lower_bp, upper_bp)):
    print(f"  Day {i:2d}: {b:+.2f} bp  [{lo:+.2f}, {hi:+.2f}]")

# ── Plot ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5))

ax.plot(periods, bwet_bp, color="#2980b9", linewidth=2.2,
        marker="o", markersize=5, label="Breakeven response (bp)")
ax.fill_between(periods, lower_bp, upper_bp,
                alpha=0.2, color="#2980b9", label="80% Confidence Band")
ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")

ax.set_xlabel("Days after BWET shock", fontsize=10)
ax.set_ylabel("10Y Breakeven response (basis points)", fontsize=10)
ax.set_title("Impulse Response: Effect of 1-SD BWET Shock on 10Y Breakeven Inflation\n"
             "How does a tanker market stress event transmit to inflation expectations?",
             fontsize=12)
ax.set_xticks(periods)
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("irf.png", dpi=150, bbox_inches="tight")
print("\nIRF chart saved as irf.png")