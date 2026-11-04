import re
from datetime import datetime
from collections import defaultdict

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "about", "against", "between", "into", "through", "during", "before", "after",
    "above", "below", "from", "up", "down", "of", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why", "how", "all",
    "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will",
    "just", "don", "should", "now", "i", "me", "my", "myself", "we", "our", "you", "your",
    "he", "she", "it", "they", "them", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did"
}

SYNONYM_DOMAINS = {
    "spending": {
        "keywords": {"buy", "buying", "bought", "purchase", "purchased", "order", "ordered", "ordering",
                     "spend", "spent", "spending", "shopping", "shop", "shopped", "cart", "checkout",
                     "amazon", "flipkart", "accessory", "accessories", "gadget", "gadgets", "item",
                     "deal", "sale", "discount", "price", "expensive", "cost", "money", "clothes", "shoes", "tech"},
        "label": "Impulsive Spending"
    },
    "sleep": {
        "keywords": {"sleep", "sleeping", "slept", "late", "midnight", "night", "stay", "staying", "stayed",
                     "awake", "bed", "rest", "insomnia", "tired", "exhausted", "scroll", "scrolling", "phone",
                     "reels", "screen", "doomscroll", "youtube", "feed"},
        "label": "Sleep Disruption"
    },
    "procrastination": {
        "keywords": {"skip", "skipping", "skipped", "delay", "delaying", "delayed", "postpone", "postponing",
                     "postponed", "procrastinate", "procrastinating", "later", "tomorrow", "avoid", "avoiding",
                     "cram", "cramming", "exam", "test", "assignment", "study", "studying", "homework", "deadline"},
        "label": "Task Procrastination"
    },
    "health": {
        "keywords": {"eat", "eating", "ate", "food", "junk", "snack", "snacking", "binge", "takeout", "delivery",
                     "sugar", "sweet", "soda", "diet", "gym", "workout", "exercise", "training", "fitness"},
        "label": "Health & Nutrition Deviation"
    },
    "social": {
        "keywords": {"argue", "argued", "arguing", "argument", "say", "saying", "said", "spoke", "speak",
                     "text", "texting", "texted", "message", "reply", "replied", "shout", "react", "reacted",
                     "snap", "snapped", "fight", "confront"},
        "label": "Impulsive Social Interaction"
    }
}

def clean_tokens(text):
    """Normalize text into lowercase alphanumeric tokens without stopwords."""
    if not text:
        return set()
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    tokens = {t.strip() for t in cleaned.split() if len(t.strip()) > 1 and t.strip() not in STOPWORDS}
    return tokens

def detect_domain(tokens):
    """Identifies matching semantic domains from tokens."""
    matched = set()
    for domain, data in SYNONYM_DOMAINS.items():
        if tokens & data["keywords"]:
            matched.add(domain)
    return matched

def calculate_time_similarity(time1, hour1, time2, hour2):
    """Calculates temporal similarity between 0.0 and 1.0."""
    time1_norm = (time1 or "").strip().lower()
    time2_norm = (time2 or "").strip().lower()

    if time1_norm and time2_norm and time1_norm == time2_norm:
        time_match = 1.0
    else:
        time_match = 0.0

    if hour1 is not None and hour2 is not None:
        diff = abs(int(hour1) - int(hour2))
        if diff > 12:
            diff = 24 - diff
        hour_score = max(0.0, 1.0 - (diff / 6.0))
    else:
        hour_score = 0.5

    return (time_match * 0.6) + (hour_score * 0.4)

def evaluate_task_against_regret(task_dict, regret_dict):
    """
    Evaluates similarity between a proposed to-do task and a historical regret.
    Returns (score: float, reasons: list of str).
    """
    task_text = task_dict.get("task", "")
    regret_text = regret_dict.get("description", "")
    task_tag = (task_dict.get("tag") or "").strip().lower()
    regret_tag = (regret_dict.get("tag") or "").strip().lower()
    task_time = task_dict.get("planned_time", "")
    task_hour = task_dict.get("planned_hour")
    regret_time = regret_dict.get("time_of_day", "")
    regret_hour = regret_dict.get("hour_of_day")

    task_tokens = clean_tokens(task_text)
    regret_tokens = clean_tokens(regret_text)

    reasons = []

    # 1. Lexical token overlap (Jaccard)
    intersection = task_tokens & regret_tokens
    union = task_tokens | regret_tokens
    jaccard = len(intersection) / len(union) if union else 0.0

    if intersection:
        reasons.append(f"Shared keywords: {', '.join(sorted(list(intersection))[:4])}")

    # 2. Semantic Domain Overlap
    task_domains = detect_domain(task_tokens)
    regret_domains = detect_domain(regret_tokens)
    domain_match = bool(task_domains & regret_domains)
    if domain_match:
        shared = task_domains & regret_domains
        domain_labels = [SYNONYM_DOMAINS[d]["label"] for d in shared if d in SYNONYM_DOMAINS]
        reasons.append(f"Shared activity pattern: {', '.join(domain_labels)}")

    # 3. Category/Tag match
    tag_score = 0.0
    if task_tag and regret_tag:
        if task_tag == regret_tag:
            tag_score = 1.0
            reasons.append(f"Matching category '{task_dict.get('tag')}'")
        elif (task_tag in regret_domains) or (regret_tag in task_domains):
            tag_score = 0.8
            reasons.append(f"Related category context ({task_tag} / {regret_tag})")

    # 4. Temporal Context
    temporal_score = calculate_time_similarity(task_time, task_hour, regret_time, regret_hour)
    if temporal_score >= 0.7:
        reasons.append(f"Similar timing context: {task_time or 'Scheduled hour'}")

    # Weighted scoring formula:
    # High synergy when domain or tags match along with time or keywords
    base_lexical = min(1.0, jaccard * 2.2) if jaccard > 0 else 0.0
    if domain_match:
        base_lexical = max(base_lexical, 0.45)

    composite_score = (
        (0.42 * base_lexical) +
        (0.33 * tag_score) +
        (0.25 * temporal_score)
    )

    # Extra reinforcement for repeated specific matches
    if domain_match and tag_score >= 0.8 and temporal_score >= 0.6:
        composite_score = min(0.98, composite_score + 0.15)

    return round(composite_score, 2), reasons

def evaluate_task(task_dict, regret_records, threshold=0.48):
    """
    Compares a candidate task against all historical regret records.
    Returns matched regrets exceeding threshold, along with personalized warning.
    """
    matches = []
    for regret in regret_records:
        score, reasons = evaluate_task_against_regret(task_dict, regret)
        if score >= threshold:
            matches.append({
                "regret_id": regret["id"],
                "regret_description": regret["description"],
                "regret_tag": regret["tag"],
                "regret_time": regret["time_of_day"],
                "regret_intensity": regret.get("intensity", 3),
                "regret_timestamp": regret.get("timestamp"),
                "score": score,
                "reasons": reasons
            })

    # Sort descending by similarity score
    matches.sort(key=lambda m: m["score"], reverse=True)

    should_warn = len(matches) > 0
    top_match = matches[0] if matches else None

    warning_data = None
    if should_warn and top_match:
        count = len(matches)
        top_desc = top_match["regret_description"]
        top_time = top_match["regret_time"]
        score_pct = int(top_match["score"] * 100)

        if count == 1:
            msg = f"Evidence Match ({score_pct}%): This task closely resembles a decision you previously regretted ('{top_desc}') during {top_time}."
        else:
            msg = f"Pattern Detected ({score_pct}% confidence): You have {count} recorded regrets with similar context (e.g. '{top_desc}')."

        warning_data = {
            "should_warn": True,
            "headline": "Wait a moment — check your past experience",
            "message": msg,
            "confidence_pct": score_pct,
            "top_match": top_match,
            "all_matches": matches[:5]
        }
    else:
        warning_data = {
            "should_warn": False,
            "message": "No significant regret pattern detected for this activity.",
            "all_matches": []
        }

    return warning_data

def discover_patterns(regret_records):
    """
    Analyzes historical regret logs and discovers recurring behavioral patterns.
    """
    if not regret_records:
        return []

    # Cluster by tag and time_of_day
    clusters = defaultdict(list)
    for r in regret_records:
        key = (r["tag"], r["time_of_day"])
        clusters[key].append(r)

    patterns = []
    for (tag, time_of_day), items in clusters.items():
        count = len(items)
        if count >= 2:
            avg_intensity = sum(i.get("intensity", 3) for i in items) / count
            sample_descs = [f"'{i['description']}'" for i in items[:2]]

            title = f"{time_of_day} {tag} Pattern"
            explanation = (
                f"You have logged {count} regrets related to {tag} during {time_of_day.lower()}. "
                f"Average regret intensity: {avg_intensity:.1f}/5. Recent examples: {', '.join(sample_descs)}."
            )

            patterns.append({
                "tag": tag,
                "title": title,
                "frequency": count,
                "context_summary": f"Peak time: {time_of_day} | Severity: {avg_intensity:.1f}/5",
                "explanation": explanation
            })

    patterns.sort(key=lambda p: p["frequency"], reverse=True)
    return patterns
