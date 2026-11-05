import os
import sys

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import init_db, get_db_connection
from backend.seed_data import seed_database
from backend.app import app

# Ensure database is initialized on startup
try:
    init_db()
    conn = get_db_connection()
    count = conn.cursor().execute("SELECT COUNT(*) FROM regrets").fetchone()[0]
    conn.close()
    if count == 0:
        seed_database()
except Exception as e:
    print(f"[!] Database startup notice: {e}", flush=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
