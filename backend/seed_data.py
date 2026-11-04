import sqlite3
import os
from .database import get_db_connection, init_db
from .engine import discover_patterns

SAMPLE_REGRETS = [
    {
        "description": "Bought an unnecessary gadget accessory online at 1:15 AM",
        "tag": "Spending",
        "time_of_day": "Late Night",
        "hour_of_day": 1,
        "intensity": 4,
        "context": "Bored in bed scrolling e-commerce flash sales, felt buyer's remorse next morning"
    },
    {
        "description": "Ordered expensive wireless headphones around midnight",
        "tag": "Spending",
        "time_of_day": "Late Night",
        "hour_of_day": 0,
        "intensity": 4,
        "context": "Already had working earphones; impulsive checkout without thinking"
    },
    {
        "description": "Purchased mechanical keyboard add-on online late at night",
        "tag": "Spending",
        "time_of_day": "Late Night",
        "hour_of_day": 2,
        "intensity": 3,
        "context": "Didn't need it, ended up returning it after shipping delay"
    },
    {
        "description": "Stayed up until 3:00 AM doomscrolling reels before BCA exam",
        "tag": "Sleep",
        "time_of_day": "Late Night",
        "hour_of_day": 3,
        "intensity": 5,
        "context": "Woke up with headache, could barely focus during 9 AM lecture"
    },
    {
        "description": "Delayed working on Python project assignment until last minute",
        "tag": "Procrastination",
        "time_of_day": "Late Night",
        "hour_of_day": 23,
        "intensity": 4,
        "context": "Stressed rushed submission with avoidable bugs"
    },
    {
        "description": "Skipped morning fitness workout to sleep in for 30 minutes",
        "tag": "Health",
        "time_of_day": "Morning",
        "hour_of_day": 7,
        "intensity": 3,
        "context": "Felt unenergetic and guilty throughout the day"
    },
    {
        "description": "Ordered greasy midnight takeout meal while gaming",
        "tag": "Health",
        "time_of_day": "Late Night",
        "hour_of_day": 1,
        "intensity": 4,
        "context": "Impulsive junk food craving, disrupted sleep schedule"
    },
    {
        "description": "Sent an impulsive emotional reply in college WhatsApp group",
        "tag": "Social",
        "time_of_day": "Evening",
        "hour_of_day": 21,
        "intensity": 4,
        "context": "Misunderstood message tone, spent 2 days feeling awkward"
    }
]

SAMPLE_TODOS = [
    {
        "task": "Review BCA Project-I architecture diagrams with professor",
        "tag": "Productivity",
        "planned_time": "Morning",
        "planned_hour": 10,
        "status": "Pending",
        "warning_triggered": 0
    },
    {
        "task": "Order wireless gaming headset online tonight",
        "tag": "Spending",
        "planned_time": "Late Night",
        "planned_hour": 0,
        "status": "Prevented",
        "warning_triggered": 1
    },
    {
        "task": "Finish reading Python SQLite documentation and test queries",
        "tag": "Study",
        "planned_time": "Afternoon",
        "planned_hour": 15,
        "status": "Completed",
        "warning_triggered": 0
    }
]

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing
    cursor.execute("DELETE FROM matches")
    cursor.execute("DELETE FROM patterns")
    cursor.execute("DELETE FROM todos")
    cursor.execute("DELETE FROM regrets")

    # Insert Regrets
    for r in SAMPLE_REGRETS:
        cursor.execute("""
            INSERT INTO regrets (description, tag, time_of_day, hour_of_day, intensity, context)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (r["description"], r["tag"], r["time_of_day"], r["hour_of_day"], r["intensity"], r["context"]))

    # Insert Todos
    for t in SAMPLE_TODOS:
        cursor.execute("""
            INSERT INTO todos (task, tag, planned_time, planned_hour, status, warning_triggered)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (t["task"], t["tag"], t["planned_time"], t["planned_hour"], t["status"], t["warning_triggered"]))

    # Discover and populate patterns
    regrets_rows = cursor.execute("SELECT * FROM regrets").fetchall()
    regrets_list = [dict(r) for r in regrets_rows]
    discovered = discover_patterns(regrets_list)

    for p in discovered:
        cursor.execute("""
            INSERT INTO patterns (tag, title, frequency, context_summary, explanation)
            VALUES (?, ?, ?, ?, ?)
        """, (p["tag"], p["title"], p["frequency"], p["context_summary"], p["explanation"]))

    conn.commit()
    conn.close()
    print("Database seeded with academic sample records successfully.")

if __name__ == "__main__":
    seed_database()
