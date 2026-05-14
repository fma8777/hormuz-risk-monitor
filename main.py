import subprocess
import sys
from datetime import datetime

def run(script):
    print(f"\n{'='*40}")
    print(f"Running {script}...")
    print(f"{'='*40}")
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: {script} failed.")
        sys.exit(1)
    print(f"{script} done.")

if __name__ == "__main__":
    start = datetime.now()
    print(f"Hormuz Risk Monitor — {start.strftime('%Y-%m-%d %H:%M')}")

    run("fetch_data.py")
    run("scrape.py")
    run("analyze.py")
    run("visualize.py")

    end = datetime.now()
    print(f"\nAll done in {(end - start).seconds} seconds.")
    print(f"Charts: hormuz_monitor.png, rolling_correlation.png")