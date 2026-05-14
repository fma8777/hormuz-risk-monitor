from dotenv import load_dotenv
import os
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

import requests
import pandas as pd
from datetime import datetime
import sqlite3

def scrape_newsapi_hormuz():
    """Search NewsAPI for Hormuz/Iran-related news headlines."""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "Hormuz OR \"Iran blockade\" OR \"strait of hormuz\"",
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 100,
        "apiKey": NEWSAPI_KEY
    }
    
    response = requests.get(url, params=params, timeout=15)
    data = response.json()
    
    articles = data.get("articles", [])
    results = []
    for a in articles:
        results.append({
            "title": a.get("title", ""),
            "pub_date": a.get("publishedAt", "")[:10],
            "source": a.get("source", {}).get("name", ""),
            "url": a.get("url", ""),
            "scraped_at": datetime.today().strftime("%Y-%m-%d")
        })
    
    df = pd.DataFrame(results).drop_duplicates(subset="title")
    keywords = ["hormuz", "iran", "blockade", "strait", "crude", "oil price"]
    df = df[df["title"].str.lower().str.contains("|".join(keywords), na=False)]
    return df

if __name__ == "__main__":
    df = scrape_newsapi_hormuz()
    print(f"Found {len(df)} relevant headlines.\n")
    print(df.to_string() if not df.empty else "No results found.")
    
    conn = sqlite3.connect("hormuz_macro.db")
    df.to_sql("eia_headlines", conn, if_exists="replace", index=False)
    conn.close()
    print("\nHeadlines saved to hormuz_macro.db → table: eia_headlines")