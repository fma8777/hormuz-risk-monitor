import pandas as pd
from fetch_data import fetch_fred_series, fetch_oil_price, merge_and_clean

df = merge_and_clean(fetch_fred_series(), fetch_oil_price())

# before and after the blockade announcement on April 13, 2026
pre  = df[df.index < "2026-04-13"]
post = df[df.index >= "2026-04-13"]

def show_corr(label, data):
    r = data["wti_chg"].corr(data["breakeven_chg"])
    print(f"{label}: oil vs breakeven correlation = {r:.3f}  (n={len(data)} days)")

show_corr("Pre-blockade  (Jan–Apr 12)", pre)
show_corr("Post-blockade (Apr 13–now)", post)