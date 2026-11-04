import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from .database import get_db_connection, init_db
from .engine import evaluate_task, discover_patterns
from .seed_data import seed_database

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)

# Ensure database is initialized
init_db()

# --- Static UI Serving ---
@app.route("/")
def serve_index():
    return send_from_directory(STATIC_DIR, "index.html")

# --- API Endpoints ---

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "REWIND Decision Assistant"})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    total_regrets = cursor.execute("SELECT COUNT(*) FROM regrets").fetchone()[0]
    total_todos = cursor.execute("SELECT COUNT(*) FROM todos").fetchone()[0]
    prevented_todos = cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'Prevented'").fetchone()[0]
    warnings_count = cursor.execute("SELECT COUNT(*) FROM todos WHERE warning_triggered = 1").fetchone()[0]
    active_todos = cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'Pending'").fetchone()[0]
    patterns_count = cursor.execute("SELECT COUNT(*) FROM patterns").fetchone()[0]

    top_tag_row = cursor.execute("""
        SELECT tag, COUNT(*) as count FROM regrets
        GROUP BY tag ORDER BY count DESC LIMIT 1
    """).fetchone()
    top_tag = top_tag_row["tag"] if top_tag_row else "None"

    conn.close()

    return jsonify({
        "total_regrets": total_regrets,
        "total_todos": total_todos,
        "active_todos": active_todos,
        "prevented_todos": prevented_todos,
        "warnings_count": warnings_count,
        "patterns_count": patterns_count,
        "top_regret_tag": top_tag
    })

# --- Regrets Endpoints ---

@app.route("/api/regrets", methods=["GET"])
def get_regrets():
    tag = request.args.get("tag")
    search = request.args.get("search")

    query = "SELECT * FROM regrets WHERE 1=1"
    params = []

    if tag and tag != "All":
        query += " AND tag = ?"
        params.append(tag)

    if search:
        query += " AND (description LIKE ? OR context LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY timestamp DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])

@app.route("/api/regrets", methods=["POST"])
def add_regret():
    data = request.json or {}
    description = (data.get("description") or "").strip()
    tag = data.get("tag", "General").strip()
    time_of_day = data.get("time_of_day", "Evening")
    hour_of_day = int(data.get("hour_of_day", 20))
    intensity = int(data.get("intensity", 3))
    context = (data.get("context") or "").strip()

    if not description:
        return jsonify({"error": "Description is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO regrets (description, tag, time_of_day, hour_of_day, intensity, context)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (description, tag, time_of_day, hour_of_day, intensity, context))
    regret_id = cursor.lastrowid

    # Re-compute patterns
    regrets_rows = cursor.execute("SELECT * FROM regrets").fetchall()
    regrets_list = [dict(r) for r in regrets_rows]
    discovered = discover_patterns(regrets_list)

    cursor.execute("DELETE FROM patterns")
    for p in discovered:
        cursor.execute("""
            INSERT INTO patterns (tag, title, frequency, context_summary, explanation)
            VALUES (?, ?, ?, ?, ?)
        """, (p["tag"], p["title"], p["frequency"], p["context_summary"], p["explanation"]))

    conn.commit()
    conn.close()

    return jsonify({"success": True, "regret_id": regret_id}), 201

@app.route("/api/regrets/<int:regret_id>", methods=["DELETE"])
def delete_regret(regret_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM regrets WHERE id = ?", (regret_id,))
    cursor.execute("DELETE FROM matches WHERE regret_id = ?", (regret_id,))

    # Update patterns
    regrets_rows = cursor.execute("SELECT * FROM regrets").fetchall()
    regrets_list = [dict(r) for r in regrets_rows]
    discovered = discover_patterns(regrets_list)
    cursor.execute("DELETE FROM patterns")
    for p in discovered:
        cursor.execute("""
            INSERT INTO patterns (tag, title, frequency, context_summary, explanation)
            VALUES (?, ?, ?, ?, ?)
        """, (p["tag"], p["title"], p["frequency"], p["context_summary"], p["explanation"]))

    conn.commit()
    conn.close()
    return jsonify({"success": True})

# --- To-Do Evaluation & Management ---

@app.route("/api/todos/evaluate", methods=["POST"])
def evaluate_candidate():
    """Real-time live comparison endpoint without persisting."""
    data = request.json or {}
    task = (data.get("task") or "").strip()
    tag = (data.get("tag") or "General").strip()
    planned_time = data.get("planned_time", "Evening")
    planned_hour = int(data.get("planned_hour", 20))

    if not task:
        return jsonify({"should_warn": False, "message": "Empty task"})

    conn = get_db_connection()
    cursor = conn.cursor()
    regret_rows = cursor.execute("SELECT * FROM regrets").fetchall()
    regrets_list = [dict(r) for r in regret_rows]
    conn.close()

    task_dict = {
        "task": task,
        "tag": tag,
        "planned_time": planned_time,
        "planned_hour": planned_hour
    }

    result = evaluate_task(task_dict, regrets_list)
    return jsonify(result)

@app.route("/api/todos", methods=["GET"])
def get_todos():
    status = request.args.get("status")
    query = "SELECT * FROM todos WHERE 1=1"
    params = []

    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])

@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.json or {}
    task = (data.get("task") or "").strip()
    tag = (data.get("tag") or "General").strip()
    planned_time = data.get("planned_time", "Evening")
    planned_hour = int(data.get("planned_hour", 20))
    user_action = data.get("user_action", "proceed") # 'proceed' or 'reconsider'

    if not task:
        return jsonify({"error": "Task description is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    regret_rows = cursor.execute("SELECT * FROM regrets").fetchall()
    regrets_list = [dict(r) for r in regret_rows]

    eval_result = evaluate_task({
        "task": task,
        "tag": tag,
        "planned_time": planned_time,
        "planned_hour": planned_hour
    }, regrets_list)

    warning_triggered = 1 if eval_result["should_warn"] else 0

    if user_action == "reconsider":
        status = "Prevented"
    else:
        status = "Pending"

    cursor.execute("""
        INSERT INTO todos (task, tag, planned_time, planned_hour, status, warning_triggered)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (task, tag, planned_time, planned_hour, status, warning_triggered))
    todo_id = cursor.lastrowid

    # Record match history if warning was triggered
    if eval_result["should_warn"]:
        for match in eval_result.get("all_matches", []):
            cursor.execute("""
                INSERT INTO matches (todo_id, regret_id, score, match_reasons, warning_shown, user_action)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (todo_id, match["regret_id"], match["score"], "; ".join(match["reasons"]), user_action))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "todo_id": todo_id,
        "status": status,
        "warning_triggered": bool(warning_triggered),
        "evaluation": eval_result
    }), 201

@app.route("/api/todos/<int:todo_id>", methods=["PATCH"])
def update_todo(todo_id):
    data = request.json or {}
    status = data.get("status")

    if not status:
        return jsonify({"error": "Status required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET status = ? WHERE id = ?", (status, todo_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    cursor.execute("DELETE FROM matches WHERE todo_id = ?", (todo_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

# --- Patterns & Seed Endpoints ---

@app.route("/api/patterns", methods=["GET"])
def get_patterns():
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM patterns ORDER BY frequency DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/seed", methods=["POST"])
def seed():
    seed_database()
    return jsonify({"success": True, "message": "Sample data seeded successfully"})

@app.route("/api/reset", methods=["POST"])
def reset():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches")
    cursor.execute("DELETE FROM patterns")
    cursor.execute("DELETE FROM todos")
    cursor.execute("DELETE FROM regrets")
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Database reset cleanly"})

# --- Static File Catch-All ---
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
