"""
Fiona Database Layer — SQLite persistence for feedback, conversations,
incidents, escalations, acknowledgments, and analytics.
"""
import sqlite3
import json
import os
import time
import threading
from typing import List, Dict, Optional
from datetime import datetime, timedelta

DB_PATH = os.getenv("FIONA_DB_PATH", "fiona.db")

_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    """Get a thread-local SQLite connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


def init_db():
    """Create all tables if they don't exist."""
    conn = _get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        message_id TEXT,
        query TEXT,
        answer TEXT,
        rating TEXT NOT NULL CHECK(rating IN ('up','down')),
        department TEXT,
        role TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        department TEXT,
        role TEXT,
        messages TEXT DEFAULT '[]',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT UNIQUE NOT NULL,
        session_id TEXT,
        department TEXT,
        role TEXT,
        incident_type TEXT NOT NULL,
        description TEXT NOT NULL,
        urgency TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'open',
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS escalations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT UNIQUE NOT NULL,
        session_id TEXT,
        department TEXT,
        role TEXT,
        query TEXT,
        conversation_context TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS acknowledgments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        department TEXT,
        role TEXT,
        policy_name TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS analytics_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        session_id TEXT,
        department TEXT,
        role TEXT,
        query TEXT,
        confidence REAL,
        data TEXT DEFAULT '{}',
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        department TEXT,
        role TEXT,
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE UNIQUE INDEX IF NOT EXISTS idx_subscriptions_email ON subscriptions(email);
    CREATE INDEX IF NOT EXISTS idx_feedback_session ON feedback(session_id);
    CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
    CREATE INDEX IF NOT EXISTS idx_analytics_type ON analytics_events(event_type);
    CREATE INDEX IF NOT EXISTS idx_analytics_created ON analytics_events(created_at);
    CREATE INDEX IF NOT EXISTS idx_analytics_dept ON analytics_events(department);
    """)
    conn.commit()


# ── Feedback ──────────────────────────────────────────────

def save_feedback(session_id: str, message_id: str, query: str, answer: str,
                  rating: str, department: str = None, role: str = None) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO feedback (session_id, message_id, query, answer, rating, department, role) VALUES (?,?,?,?,?,?,?)",
        (session_id, message_id, query, answer, rating, department, role)
    )
    conn.commit()
    return cur.lastrowid


def get_feedback_stats(days: int = 30) -> Dict:
    conn = _get_conn()
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT rating, COUNT(*) as cnt FROM feedback WHERE created_at >= ? GROUP BY rating", (since,)
    ).fetchall()
    stats = {"up": 0, "down": 0, "total": 0}
    for r in rows:
        stats[r["rating"]] = r["cnt"]
        stats["total"] += r["cnt"]
    if stats["total"] > 0:
        stats["satisfaction_pct"] = round(stats["up"] / stats["total"] * 100, 1)
    else:
        stats["satisfaction_pct"] = 0
    return stats


# ── Conversations ─────────────────────────────────────────

def save_conversation(session_id: str, messages: List[Dict],
                      department: str = None, role: str = None):
    conn = _get_conn()
    msgs_json = json.dumps(messages)
    conn.execute("""
        INSERT INTO conversations (session_id, department, role, messages, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(session_id) DO UPDATE SET
            messages = excluded.messages,
            updated_at = datetime('now')
    """, (session_id, department, role, msgs_json))
    conn.commit()


def get_conversation(session_id: str) -> Optional[Dict]:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM conversations WHERE session_id = ?", (session_id,)
    ).fetchone()
    if row:
        return {**dict(row), "messages": json.loads(row["messages"])}
    return None


# ── Incidents ─────────────────────────────────────────────

def save_incident(session_id: str, incident_type: str, description: str,
                  urgency: str = "medium", department: str = None,
                  role: str = None) -> Dict:
    # Use SQLite's AUTOINCREMENT rowid as the unique counter — avoids race
    # conditions from global in-process counters under concurrent requests.
    conn = _get_conn()
    date_str = datetime.utcnow().strftime('%Y%m%d')
    # Insert a temporary unique reference, then update to the real one once
    # we know the stable rowid.
    cur = conn.execute(
        "INSERT INTO incidents (reference, session_id, department, role, incident_type, description, urgency) VALUES (?,?,?,?,?,?,?)",
        (f"INC-{date_str}-PENDING-{os.urandom(4).hex()}", session_id, department, role, incident_type, description, urgency)
    )
    rowid = cur.lastrowid
    ref = f"INC-{date_str}-{rowid:04d}"
    conn.execute("UPDATE incidents SET reference=? WHERE id=?", (ref, rowid))
    conn.commit()
    return {"reference": ref, "status": "open"}


def get_incidents(limit: int = 50) -> List[Dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


# ── Escalations ───────────────────────────────────────────

def save_escalation(session_id: str, query: str, conversation_context: str,
                    department: str = None, role: str = None) -> Dict:
    conn = _get_conn()
    date_str = datetime.utcnow().strftime('%Y%m%d')
    cur = conn.execute(
        "INSERT INTO escalations (reference, session_id, department, role, query, conversation_context) VALUES (?,?,?,?,?,?)",
        (f"ESC-{date_str}-PENDING-{os.urandom(4).hex()}", session_id, department, role, query, conversation_context)
    )
    rowid = cur.lastrowid
    ref = f"ESC-{date_str}-{rowid:04d}"
    conn.execute("UPDATE escalations SET reference=? WHERE id=?", (ref, rowid))
    conn.commit()
    return {"reference": ref, "status": "pending"}


# ── Acknowledgments ───────────────────────────────────────

def save_acknowledgment(session_id: str, policy_name: str,
                        department: str = None, role: str = None) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO acknowledgments (session_id, department, role, policy_name) VALUES (?,?,?,?)",
        (session_id, department, role, policy_name)
    )
    conn.commit()
    return cur.lastrowid


def get_acknowledgment_stats() -> List[Dict]:
    conn = _get_conn()
    rows = conn.execute("""
        SELECT policy_name, department, COUNT(*) as count
        FROM acknowledgments
        GROUP BY policy_name, department
        ORDER BY count DESC
    """).fetchall()
    return [dict(r) for r in rows]


# ── Analytics ─────────────────────────────────────────────

def log_event(event_type: str, session_id: str = None, department: str = None,
              role: str = None, query: str = None, confidence: float = None,
              data: Dict = None):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO analytics_events (event_type, session_id, department, role, query, confidence, data) VALUES (?,?,?,?,?,?,?)",
        (event_type, session_id, department, role, query, confidence, json.dumps(data or {}))
    )
    conn.commit()


def get_analytics_summary(days: int = 30) -> Dict:
    conn = _get_conn()
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()

    total = conn.execute(
        "SELECT COUNT(*) as cnt FROM analytics_events WHERE event_type='chat' AND created_at >= ?", (since,)
    ).fetchone()["cnt"]

    by_dept = conn.execute(
        "SELECT department, COUNT(*) as cnt FROM analytics_events WHERE event_type='chat' AND created_at >= ? AND department IS NOT NULL GROUP BY department ORDER BY cnt DESC",
        (since,)
    ).fetchall()

    daily = conn.execute(
        "SELECT date(created_at) as day, COUNT(*) as cnt FROM analytics_events WHERE event_type='chat' AND created_at >= ? GROUP BY day ORDER BY day",
        (since,)
    ).fetchall()

    low_conf = conn.execute(
        "SELECT query, confidence, department, created_at FROM analytics_events WHERE event_type='chat' AND confidence IS NOT NULL AND confidence < 0.4 AND created_at >= ? ORDER BY confidence ASC LIMIT 20",
        (since,)
    ).fetchall()

    feedback = get_feedback_stats(days)

    return {
        "total_queries": total,
        "by_department": [dict(r) for r in by_dept],
        "daily_volume": [dict(r) for r in daily],
        "low_confidence_queries": [dict(r) for r in low_conf],
        "feedback": feedback,
    }


def get_popular_questions(department: str = None, limit: int = 10) -> List[Dict]:
    conn = _get_conn()
    if department:
        rows = conn.execute(
            "SELECT query, COUNT(*) as cnt FROM analytics_events WHERE event_type='chat' AND department=? AND query IS NOT NULL GROUP BY query ORDER BY cnt DESC LIMIT ?",
            (department, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT query, COUNT(*) as cnt FROM analytics_events WHERE event_type='chat' AND query IS NOT NULL GROUP BY query ORDER BY cnt DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Subscriptions ─────────────────────────────────────────

def subscribe(email: str, department: str = None, role: str = None) -> bool:
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO subscriptions (email, department, role) VALUES (?, ?, ?) ON CONFLICT(email) DO UPDATE SET active=1, department=excluded.department, role=excluded.role",
            (email, department, role)
        )
        conn.commit()
        return True
    except Exception:
        return False


def unsubscribe(email: str) -> bool:
    conn = _get_conn()
    conn.execute("UPDATE subscriptions SET active=0 WHERE email=?", (email,))
    conn.commit()
    return True


def get_active_subscribers() -> List[Dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM subscriptions WHERE active=1").fetchall()
    return [dict(r) for r in rows]


def get_digest_data(department: str = None) -> Dict:
    """Compile data for a weekly digest email."""
    conn = _get_conn()
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

    query_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM analytics_events WHERE event_type='chat' AND created_at >= ?",
        (week_ago,)
    ).fetchone()["cnt"]

    popular = get_popular_questions(department, limit=5)
    fb = get_feedback_stats(7)
    gaps = get_kb_gaps(5)

    return {
        "period": "Last 7 days",
        "total_queries": query_count,
        "popular_questions": popular,
        "feedback": fb,
        "kb_gaps": gaps,
    }


def get_kb_gaps(limit: int = 20) -> List[Dict]:
    """Queries with low confidence OR thumbs-down feedback."""
    conn = _get_conn()
    # Low confidence queries
    low_conf = conn.execute("""
        SELECT query, confidence, department, 'low_confidence' as reason
        FROM analytics_events
        WHERE event_type='chat' AND confidence IS NOT NULL AND confidence < 0.35
        ORDER BY created_at DESC LIMIT ?
    """, (limit,)).fetchall()

    # Thumbs-down queries
    thumbs_down = conn.execute("""
        SELECT query, 0 as confidence, department, 'negative_feedback' as reason
        FROM feedback WHERE rating='down'
        ORDER BY created_at DESC LIMIT ?
    """, (limit,)).fetchall()

    results = [dict(r) for r in low_conf] + [dict(r) for r in thumbs_down]
    # Deduplicate by query
    seen = set()
    unique = []
    for r in results:
        q = (r.get("query") or "").strip().lower()
        if q and q not in seen:
            seen.add(q)
            unique.append(r)
    return unique[:limit]
