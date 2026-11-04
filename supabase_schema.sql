-- ====================================================================
-- REWIND: AI-Based Personal Decision and Regret Pattern Assistant
-- Supabase / PostgreSQL Schema Definition
-- Course: Project-I (B308) | Session 2026-27 | BCA-3rd Semester
-- ====================================================================

-- 1. Regrets Table (Retrospective Historical Evidence)
CREATE TABLE IF NOT EXISTS public.regrets (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    description TEXT NOT NULL,
    tag TEXT NOT NULL DEFAULT 'General',
    time_of_day TEXT NOT NULL DEFAULT 'Evening',
    hour_of_day INT2 DEFAULT 20 CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
    intensity INT2 DEFAULT 3 CHECK (intensity >= 1 AND intensity <= 5),
    context TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 2. Todos Table (Upcoming Planned Activities & Decisions)
CREATE TABLE IF NOT EXISTS public.todos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    task TEXT NOT NULL,
    tag TEXT NOT NULL DEFAULT 'General',
    planned_time TEXT NOT NULL DEFAULT 'Evening',
    planned_hour INT2 DEFAULT 20 CHECK (planned_hour >= 0 AND planned_hour <= 23),
    status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Prevented', 'Completed', 'Cancelled')),
    warning_triggered BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 3. Matches Table (Evidence Linkage Between Current Action & Past Regret)
CREATE TABLE IF NOT EXISTS public.matches (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    todo_id BIGINT REFERENCES public.todos(id) ON DELETE CASCADE,
    regret_id BIGINT REFERENCES public.regrets(id) ON DELETE CASCADE,
    score NUMERIC(4, 2) NOT NULL,
    match_reasons TEXT,
    warning_shown BOOLEAN DEFAULT TRUE NOT NULL,
    user_action TEXT DEFAULT 'pending' CHECK (user_action IN ('pending', 'proceed', 'reconsider', 'dismissed')),
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 4. Patterns Table (Discovered Recurring Behavioral Traps)
CREATE TABLE IF NOT EXISTS public.patterns (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tag TEXT NOT NULL,
    title TEXT NOT NULL,
    frequency INT4 DEFAULT 1 NOT NULL,
    context_summary TEXT,
    explanation TEXT,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- ====================================================================
-- Performance Indexes
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_regrets_tag ON public.regrets(tag);
CREATE INDEX IF NOT EXISTS idx_regrets_time_of_day ON public.regrets(time_of_day);
CREATE INDEX IF NOT EXISTS idx_regrets_created_at ON public.regrets(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_todos_status ON public.todos(status);
CREATE INDEX IF NOT EXISTS idx_todos_tag ON public.todos(tag);
CREATE INDEX IF NOT EXISTS idx_todos_created_at ON public.todos(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_matches_todo_id ON public.matches(todo_id);
CREATE INDEX IF NOT EXISTS idx_matches_regret_id ON public.matches(regret_id);

CREATE INDEX IF NOT EXISTS idx_patterns_frequency ON public.patterns(frequency DESC);

-- ====================================================================
-- Enable Row Level Security (RLS) & Default Access Policies
-- ====================================================================
ALTER TABLE public.regrets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.todos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patterns ENABLE ROW LEVEL SECURITY;

-- Allow read/write access for application usage (anon / authenticated)
CREATE POLICY "Allow anon read regrets" ON public.regrets FOR SELECT USING (true);
CREATE POLICY "Allow anon insert regrets" ON public.regrets FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update regrets" ON public.regrets FOR UPDATE USING (true);
CREATE POLICY "Allow anon delete regrets" ON public.regrets FOR DELETE USING (true);

CREATE POLICY "Allow anon read todos" ON public.todos FOR SELECT USING (true);
CREATE POLICY "Allow anon insert todos" ON public.todos FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update todos" ON public.todos FOR UPDATE USING (true);
CREATE POLICY "Allow anon delete todos" ON public.todos FOR DELETE USING (true);

CREATE POLICY "Allow anon read matches" ON public.matches FOR SELECT USING (true);
CREATE POLICY "Allow anon insert matches" ON public.matches FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update matches" ON public.matches FOR UPDATE USING (true);
CREATE POLICY "Allow anon delete matches" ON public.matches FOR DELETE USING (true);

CREATE POLICY "Allow anon read patterns" ON public.patterns FOR SELECT USING (true);
CREATE POLICY "Allow anon insert patterns" ON public.patterns FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update patterns" ON public.patterns FOR UPDATE USING (true);
CREATE POLICY "Allow anon delete patterns" ON public.patterns FOR DELETE USING (true);

-- ====================================================================
-- Optional Academic Pre-Seeded Dataset (Matches Project-I Synopsis)
-- ====================================================================
INSERT INTO public.regrets (description, tag, time_of_day, hour_of_day, intensity, context) VALUES
('Bought an unnecessary gadget accessory online at 1:15 AM', 'Spending', 'Late Night', 1, 4, 'Bored in bed scrolling e-commerce flash sales, felt buyer remorse next morning'),
('Ordered expensive wireless headphones around midnight', 'Spending', 'Late Night', 0, 4, 'Already had working earphones; impulsive checkout without thinking'),
('Purchased mechanical keyboard add-on online late at night', 'Spending', 'Late Night', 2, 3, 'Didn''t need it, ended up returning it after shipping delay'),
('Stayed up until 3:00 AM doomscrolling reels before BCA exam', 'Sleep', 'Late Night', 3, 5, 'Woke up with headache, could barely focus during 9 AM lecture'),
('Delayed working on Python project assignment until last minute', 'Procrastination', 'Late Night', 23, 4, 'Stressed rushed submission with avoidable bugs'),
('Skipped morning fitness workout to sleep in for 30 minutes', 'Health', 'Morning', 7, 3, 'Felt unenergetic and guilty throughout the day'),
('Ordered greasy midnight takeout meal while gaming', 'Health', 'Late Night', 1, 4, 'Impulsive junk food craving, disrupted sleep schedule'),
('Sent an impulsive emotional reply in college WhatsApp group', 'Social', 'Evening', 21, 4, 'Misunderstood message tone, spent 2 days feeling awkward');

INSERT INTO public.todos (task, tag, planned_time, planned_hour, status, warning_triggered) VALUES
('Review BCA Project-I architecture diagrams with professor', 'Productivity', 'Morning', 10, 'Pending', FALSE),
('Order wireless gaming headset online tonight', 'Spending', 'Late Night', 0, 'Prevented', TRUE),
('Finish reading Python SQLite documentation and test queries', 'Study', 'Afternoon', 15, 'Completed', FALSE);

INSERT INTO public.patterns (tag, title, frequency, context_summary, explanation) VALUES
('Spending', 'Late Night Spending Pattern', 3, 'Peak time: Late Night | Severity: 3.7/5', 'You have logged 3 regrets related to Spending during late night. Average regret intensity: 3.7/5. Recent examples: gadget accessory purchase, expensive wireless headphones.');
