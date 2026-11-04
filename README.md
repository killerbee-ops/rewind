# REWIND: An AI-Based Personal Decision and Regret Pattern Assistant

> **BCA-3rd Semester (Session 2026-27)**  
> **Course**: Project-I (B308)  
> **Submitted By**: Tanish Jaswal (Roll No: 13250545)  
> **Submitted To**: Dr. Poonam Singh, Assistant Professor  
> **Institution**: M.M. Institute of Computer Technology & Business Management, Maharishi Markandeshwar (Deemed to be University), Mullana–Ambala, Haryana (India)

---

## 🌟 Overview

**REWIND** is a personal decision-support application built around a simple but rarely used source of guidance: **the user’s own history of regret**. Instead of predicting universal "good" behavior or imposing moral rules, REWIND compares upcoming to-do items and planned decisions with previously logged situations that the user explicitly marked as regrettable.

The system adheres strictly to the architectural design principle: **"Intervene only on evidence"** — remaining completely silent when evidence is weak, and surfacing concise, evidence-based alerts when a meaningful pattern is detected.

---

## 🎨 Theme & Visual Style

Designed with a **Bright Glassy Theme (Glassmorphism)**:
- **Luminous Aurora Backdrop**: High-contrast, vibrant pastel mesh gradients with smooth ambient floating glow orbs.
- **Frosted Translucent Glass Panels**: `backdrop-filter: blur(24px) saturate(180%)`, milky glass card layers, glowing borders, and specular highlights.
- **Real-Time Live Typing Scanner**: Dynamic evidence check bar with glowing pulse indicator that scans past regrets as you type.
- **Frosted Warning Shield Modal**: Presents similarity scores, citations of exact past regret memories, and choices (*"Reconsider & Prevent"* vs *"Proceed Anyway"*).

---

## 🚀 Quick Start (Running Locally)

### Prerequisites
- Python 3.9+ (Python 3.14+ supported)
- Flask and Flask-CORS

### Installation

```bash
# 1. Navigate to the project root
cd "d:/ai project"

# 2. Install minimal dependencies
pip install -r requirements.txt

# 3. Launch the application
python run.py
```

The script will automatically initialize the local SQLite database, populate academic sample records from the synopsis, and launch your browser at:
`http://127.0.0.1:5000`

---

## 📂 Project Structure

```
d:/ai project/
├── backend/
│   ├── app.py              # Flask REST API endpoints and static file routing
│   ├── database.py         # SQLite connection manager and schema DDL
│   ├── engine.py           # Multi-factor pattern matching & relevance engine
│   └── seed_data.py        # Synopsis academic seed scenarios
├── static/
│   ├── index.html          # Responsive single page application UI
│   ├── css/
│   │   └── glassy.css      # Bright glassmorphism styling & animations
│   └── js/
│       ├── api.js          # Asynchronous backend API client
│       └── app.js          # Real-time typing scanner and UI state manager
├── requirements.txt        # Backend dependencies
├── run.py                  # Single-command launcher script with auto-browser
└── README.md               # Project documentation
```

---

## 🧠 System Architecture & Methodology

```
┌─────────────────┐       ┌─────────────────┐
│ Planned To-Do   │       │ Regret History  │
│ (Task & Context)│       │ (Logged Regrets)│
└────────┬────────┘       └────────┬────────┘
         │                         │
         ▼                         ▼
   ┌─────────────────────────────────────┐
   │    Pattern Matching Engine          │
   │  • Lexical Overlap (Jaccard)        │
   │  • Semantic Domain Clustered Synonyms│
   │  • Category Tag Alignment           │
   │  • Temporal Context (Hour & Time)   │
   └──────────────────┬──────────────────┘
                      │
                      ▼
         [ Score >= Threshold (0.48)? ]
                 /          \
               Yes           No
               /              \
              ▼                ▼
     ┌─────────────────┐  ┌──────────────┐
     │ Evidence Warning│  │ Remain Silent│
     │  Modal Shown    │  └──────────────┘
     └────────┬────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
[Reconsider]      [Proceed]
(Prevented)       (Pending)
```

### Data Schema (SQLite)
1. **`regrets`**: `id`, `description`, `tag`, `time_of_day`, `hour_of_day`, `intensity`, `context`, `timestamp`
2. **`todos`**: `id`, `task`, `tag`, `planned_time`, `planned_hour`, `status`, `warning_triggered`, `created_at`
3. **`matches`**: `id`, `todo_id`, `regret_id`, `score`, `match_reasons`, `warning_shown`, `user_action`, `created_at`
4. **`patterns`**: `id`, `tag`, `title`, `frequency`, `context_summary`, `explanation`, `updated_at`

---

## 🧪 Built-in Demonstration Scenarios

Click any chip in the **Quick Test Scenarios** bar at the top of the app:
1. **🎧 Late-Night Headphones Purchase**: Matches past 1 AM impulsive shopping regrets $\to$ Warning triggered with 85%+ confidence.
2. **📱 Late Reels Before Exam**: Matches past 3 AM sleep disruption regrets $\to$ Warning triggered.
3. **⏳ Postpone Project Work**: Matches past last-minute assignment submission panic $\to$ Warning triggered.
4. **📚 Safe Morning Study**: Regular daytime study session $\to$ Zero false warning (Silent pass).
