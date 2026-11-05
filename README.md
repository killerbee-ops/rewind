# REWIND: An AI-Based Personal Decision and Regret Pattern Assistant

> **BCA-3rd Semester (Session 2026-27)**  
> **Course**: Project-I (B308)  
> **Submitted By**: Tanish Jaswal (Roll No: 13250545)  
> **Submitted To**: Dr. Poonam Singh, Assistant Professor  
> **Institution**: M.M. Institute of Computer Technology & Business Management, Maharishi Markandeshwar (Deemed to be University), Mullana–Ambala, Haryana (India)

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/killerbee-ops/rewind)
[![Supabase Database](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/dashboard)
[![Python 3.14](https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

---

### 🔗 Project & Database Links
- 📦 **GitHub Repository**: [https://github.com/killerbee-ops/rewind](https://github.com/killerbee-ops/rewind)
- ⚡ **Supabase Dashboard**: [https://supabase.com/dashboard](https://supabase.com/dashboard)
- 📄 **Supabase PostgreSQL Schema**: [`supabase_schema.sql`](supabase_schema.sql)
- 🌐 **Local Web App**: [http://127.0.0.1:5050](http://127.0.0.1:5050)

---

## 🌟 Overview

**REWIND** is a personal decision-support application built around a simple but rarely used source of guidance: **the user’s own history of regret**. Instead of predicting universal "good" behavior or imposing moral rules, REWIND compares upcoming to-do items and planned decisions with previously logged situations that the user explicitly marked as regrettable.

The system adheres strictly to the architectural design principle: **"Intervene only on evidence"** — remaining completely silent when evidence is weak, and surfacing concise, evidence-based alerts when a meaningful pattern is detected.

---

## 🎨 Theme & Visual Style

Designed with a **Bright Glassy Theme (Glassmorphism)**:
- **Luminous Aurora Backdrop**: High-contrast, vibrant pastel mesh gradients with smooth ambient floating glow orbs.
- **Frosted Translucent Glass Panels**: `backdrop-filter: blur(20px) saturate(180%)`, milky glass card layers, glowing borders, and specular highlights.
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

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the application
python run.py
```

The script will automatically initialize the local SQLite database, populate academic sample records from the synopsis, and launch your browser at:
`http://127.0.0.1:5000`

---

## ⚡ Supabase Database Setup

A ready-to-run Supabase PostgreSQL schema script is provided in **[`supabase_schema.sql`](supabase_schema.sql)**.

### How to Apply to Supabase:
1. Open your project on [Supabase Dashboard](https://supabase.com/dashboard).
2. Go to the **SQL Editor** tab from the left sidebar.
3. Click **New Query**, paste the full contents of `supabase_schema.sql`, and click **Run**.
4. All 4 tables (`regrets`, `todos`, `matches`, `patterns`), indexes, RLS policies, and academic seed records will be created instantly.

### Supabase Table Schema Overview:
| Table Name | Description | Key Columns |
| :--- | :--- | :--- |
| **`regrets`** | Historical retrospective records | `id`, `description`, `tag`, `time_of_day`, `hour_of_day`, `intensity`, `context`, `created_at` |
| **`todos`** | Upcoming decisions & actions | `id`, `task`, `tag`, `planned_time`, `planned_hour`, `status`, `warning_triggered`, `created_at` |
| **`matches`** | Linkage between current action and regret | `id`, `todo_id`, `regret_id`, `score`, `match_reasons`, `warning_shown`, `user_action`, `created_at` |
| **`patterns`** | Clustered behavioral vulnerabilities | `id`, `tag`, `title`, `frequency`, `context_summary`, `explanation`, `updated_at` |

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
├── supabase_schema.sql     # Ready-to-run Supabase / PostgreSQL schema script
├── .env.example            # Environment variables template for Supabase
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

---

## 🧪 Built-in Demonstration Scenarios

Click any chip in the **⚡ Try:** picker at the top of the app:
1. **Headphones Purchase**: Matches past 1 AM impulsive shopping regrets $\to$ Warning triggered with 85%+ confidence.
2. **Reels Before Exam**: Matches past 3 AM sleep disruption regrets $\to$ Warning triggered.
3. **Delay Project Work**: Matches past last-minute assignment submission panic $\to$ Warning triggered.
4. **Safe Study**: Regular daytime study session $\to$ Zero false warning (Silent pass).
