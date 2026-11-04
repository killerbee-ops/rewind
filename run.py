import os
import sys
import webbrowser
import threading
import time

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db, get_db_connection
from backend.seed_data import seed_database
from backend.app import app

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:5000"
    print(f"\n[+] Opening REWIND Assistant in browser: {url}\n", flush=True)
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[!] Could not open browser automatically: {e}", flush=True)

if __name__ == "__main__":
    print("=" * 65, flush=True)
    print("  REWIND - AI Personal Decision & Regret Pattern Assistant", flush=True)
    print("  BCA-3rd Semester (Session 2026-27) | Project-I (B308)", flush=True)
    print("  Theme: Bright Glassy Glassmorphism | Fast SQLite + Flask", flush=True)
    print("=" * 65, flush=True)

    # Initialize DB
    init_db()

    # Pre-seed if regrets are empty
    conn = get_db_connection()
    count = conn.cursor().execute("SELECT COUNT(*) FROM regrets").fetchone()[0]
    conn.close()

    if count == 0:
        print("[+] Pre-seeding database with academic demonstration records...", flush=True)
        seed_database()
    else:
        print(f"[+] Loaded existing database ({count} regret records found).", flush=True)

    # Launch browser thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask Server
    print("[+] Starting local server on http://127.0.0.1:5000 ... (Press CTRL+C to stop)", flush=True)
    app.run(host="127.0.0.1", port=5000, debug=False)
