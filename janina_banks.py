"""
janina_banks.py — HR Response Store + Customer Feedback + Email Submission Handler
====================================================================================
Thin Postgres helper for:
  - Storing updated HR responses indexed by category/query type.
  - Logging customer complaints and feedback.
  - Storing email submissions from web form.
  - Quick retrieval of responses by domain/keyword.

Assumes:
  - A Postgres DATABASE_URL in the environment, e.g.
    postgres://user:password@host:5432/janina_prod
  - Table janina_responses created by migration V001.
  - Table janina_feedback created by migration V002.
  - Table janina_submissions created by migration V003.
"""

import os
import logging
import datetime
from typing import List, Dict, Optional

import psycopg2
import psycopg2.extras

logger = logging.getLogger("janina_banks")

# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_db_conn():
    """
    Open a new Postgres connection using DATABASE_URL.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set in environment.")
    return psycopg2.connect(db_url)


# ---------------------------------------------------------------------------
# Auto-create responses table
# ---------------------------------------------------------------------------

def ensure_responses_table():
    """
    Idempotently create janina_responses if it doesn't exist yet.
    Stores HR responses indexed by category and searchable keywords.
    Safe to call on every startup.
    """
    sql = """
        CREATE TABLE IF NOT EXISTS janina_responses (
            id              SERIAL PRIMARY KEY,
            category        TEXT NOT NULL,
            query_type      TEXT,
            keywords        TEXT[],
            response_text   TEXT NOT NULL,
            quality_score   FLOAT DEFAULT 0.0,
            active          BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT now(),
            updated_at      TIMESTAMPTZ DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS idx_responses_category
            ON janina_responses (category) WHERE active = TRUE;
        CREATE INDEX IF NOT EXISTS idx_responses_fts
            ON janina_responses
            USING gin(to_tsvector('english',
                coalesce(category,'') || ' ' ||
                coalesce(query_type,'') || ' ' ||
                coalesce(response_text,'')));
    """
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        logger.info("janina_responses table ensured.")
    except Exception as e:
        logger.warning("Could not ensure responses table: %s", e)


# ---------------------------------------------------------------------------
# Auto-create feedback table
# ---------------------------------------------------------------------------

def ensure_feedback_table():
    """
    Idempotently create janina_feedback if it doesn't exist yet.
    Stores customer complaints and feedback.
    Safe to call on every startup.
    """
    sql = """
        CREATE TABLE IF NOT EXISTS janina_feedback (
            id              SERIAL PRIMARY KEY,
            feedback_type   TEXT NOT NULL,
            sentiment       TEXT,
            complaint_text  TEXT,
            priority        INT DEFAULT 0,
            status          TEXT DEFAULT 'open',
            created_at      TIMESTAMPTZ DEFAULT now(),
            resolved_at     TIMESTAMPTZ
        );
        CREATE INDEX IF NOT EXISTS idx_feedback_type
            ON janina_feedback (feedback_type);
        CREATE INDEX IF NOT EXISTS idx_feedback_status
            ON janina_feedback (status);
        CREATE INDEX IF NOT EXISTS idx_feedback_priority
            ON janina_feedback (priority DESC);
    """
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        logger.info("janina_feedback table ensured.")
    except Exception as e:
        logger.warning("Could not ensure feedback table: %s", e)


# ---------------------------------------------------------------------------
# Auto-create submissions table (emails from web form)
# ---------------------------------------------------------------------------

def ensure_submissions_table():
    """
    Idempotently create janina_submissions if it doesn't exist yet.
    Stores email addresses and form submissions from the website.
    Safe to call on every startup.
    """
    sql = """
        CREATE TABLE IF NOT EXISTS janina_submissions (
            id              SERIAL PRIMARY KEY,
            email           TEXT NOT NULL,
            name            TEXT,
            subject         TEXT,
            message         TEXT,
            form_data       JSONB,
            ip_address      TEXT,
            user_agent      TEXT,
            status          TEXT DEFAULT 'received',
            created_at      TIMESTAMPTZ DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS idx_submissions_email
            ON janina_submissions (email);
        CREATE INDEX IF NOT EXISTS idx_submissions_status
            ON janina_submissions (status);
        CREATE INDEX IF NOT EXISTS idx_submissions_created
            ON janina_submissions (created_at DESC);
    """
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        logger.info("janina_submissions table ensured.")
    except Exception as e:
        logger.warning("Could not ensure submissions table: %s", e)


# ---------------------------------------------------------------------------
# Ensure ALL tables
# ---------------------------------------------------------------------------

def ensure_all_tables():
    """
    Ensure all Janina tables exist. Call once on startup.
    Graceful — each table creation is independent.
    """
    ensure_responses_table()
    ensure_feedback_table()
    ensure_submissions_table()


# ---------------------------------------------------------------------------
# Store/Retrieve HR Responses
# ---------------------------------------------------------------------------

def store_response(
    category: str,
    query_type: str,
    keywords: List[str],
    response_text: str,
    quality_score: float = 0.0,
    active: bool = True,
) -> bool:
    """
    Store a single HR response.
    
    Args:
        category:       e.g., 'benefits', 'payroll', 'hiring'
        query_type:     e.g., 'faq', 'complaint', 'request'
        keywords:       searchable tags, e.g., ['vacation', 'policy']
        response_text:  the actual response
        quality_score:  relevance/quality metric (0.0-1.0)
        active:         whether this response is in use
    
    Returns:
        True if stored successfully, False on error.
    """
    sql = """
        INSERT INTO janina_responses
            (category, query_type, keywords, response_text, quality_score, active)
        VALUES
            (%s, %s, %s, %s, %s, %s)
    """
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (category, query_type, keywords, response_text,
                                  quality_score, active))
            conn.commit()
        logger.info("Response stored [%s, %s]: %s", category, query_type,
                    ", ".join(keywords[:2]))
        return True
    except Exception as e:
        logger.error("Failed to store response: %s", e)
        return False


def get_response_by_category(category: str, limit: int = 5) -> List[Dict]:
    """
    Retrieve active responses in a given category.
    
    Args:
        category:  the category to search
        limit:     max results
    
    Returns:
        List of response dicts, or empty list on error.
    """
    sql = """
        SELECT id, category, query_type, keywords, response_text, quality_score
        FROM janina_responses
        WHERE category = %s AND active = TRUE
        ORDER BY quality_score DESC
        LIMIT %s
    """
    try:
        with get_db_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, (category, limit))
                rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("Failed to get responses by category: %s", e)
        return []


def search_responses_by_keyword(keyword: str, limit: int = 10) -> List[Dict]:
    """
    Full-text search responses by keyword.
    
    Args:
        keyword:  the search term
        limit:    max results
    
    Returns:
        List of matching responses, or empty list on error.
    """
    sql = """
        SELECT id, category, query_type, keywords, response_text, quality_score
        FROM janina_responses
        WHERE active = TRUE
          AND to_tsvector('english', response_text || ' ' || array_to_string(keywords, ' '))
              @@ plainto_tsquery('english', %s)
        ORDER BY quality_score DESC
        LIMIT %s
    """
    try:
        with get_db_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, (keyword, limit))
                rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("Failed to search responses: %s", e)
        return []


def get_all_responses(limit: int = None) -> List[Dict]:
    """
    Retrieve all active responses (useful for bulk sync or admin views).
    
    Args:
        limit:  max results (None = all)
    
    Returns:
        List of all active responses.
    """
    sql = """
        SELECT id, category, query_type, keywords, response_text, quality_score, created_at
        FROM janina_responses
        WHERE active = TRUE
        ORDER BY updated_at DESC
    """
    if limit:
        sql += f" LIMIT {limit}"
    
    try:
        with get_db_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("Failed to get all responses: %s", e)
        return []


# ---------------------------------------------------------------------------
# Store/Retrieve Feedback
# ---------------------------------------------------------------------------

def store_feedback(
    feedback_type: str,
    complaint_text: str,
    sentiment: str = "neutral",
    priority: int = 0,
) -> bool:
    """
    Store customer feedback or complaint.
    
    Args:
        feedback_type:   e.g., 'complaint', 'suggestion', 'bug'
        complaint_text:  the actual feedback
        sentiment:       'positive', 'neutral', 'negative'
        priority:        numeric priority (higher = more urgent)
    
    Returns:
        True if stored successfully, False on error.
    """
    sql = """
        INSERT INTO janina_feedback
            (feedback_type, complaint_text, sentiment, priority)
        VALUES
            (%s, %s, %s, %s)
    """
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (feedback_type, complaint_text, sentiment, priority))
            conn.commit()
        logger.info("Feedback stored [%s, sentiment=%s]", feedback_type, sentiment)
        return True
    except Exception as e:
        logger.error("Failed to store feedback: %s", e)
        return False


def get_feedback_by_status(status: str, limit: int = 20) -> List[Dict]:
    """
    Retrieve feedback by status (e.g., 'open', 'resolved').
    
    Args:
        status:  the status to filter by
        limit:   max results
    
    Returns:
        List of feedback dicts.
    """
    sql = """
        SELECT id, feedback_type, sentiment, complaint_text, priority, status, created_at
        FROM janina_feedback
        WHERE status = %s
        ORDER BY priority DESC, created_at DESC
        LIMIT %s
    """
    try:
        with get_db_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, (status, limit))
                rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("Failed to get feedback: %s", e)
        return []


# ---------------------------------------------------------------------------
# Store/Retrieve Form Submissions
# ---------------------------------------------------------------------------

def store_submission(
    email: str,
    name: str = None,
    subject: str = None,
    message: str = None,
    form_data: Dict = None,
    ip_address: str = None,
    user_agent: str = None,
) -> bool:
    """
    Store an email submission from the web form.
    
    Args:
        email:       customer email address (required)
        name:        customer name (optional)
        subject:     message subject (optional)
        message:     message body (optional)
        form_data:   full form payload as JSON dict (optional)
        ip_address:  client IP for tracking (optional)
        user_agent:  browser user agent (optional)
    
    Returns:
        True if stored successfully, False on error.
    """
    import json
    
    sql = """
        INSERT INTO janina_submissions
            (email, name, subject, message, form_data, ip_address, user_agent)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        form_json = json.dumps(form_data) if form_data else None
        
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (email, name, subject, message, form_json,
                                  ip_address, user_agent))
            conn.commit()
        logger.info("Submission stored [%s]: %s", email, subject or "no subject")
        return True
    except Exception as e:
        logger.error("Failed to store submission: %s", e)
        return False


def get_submissions(status: str = None, limit: int = 50) -> List[Dict]:
    """
    Retrieve form submissions, optionally filtered by status.
    
    Args:
        status:  filter by status (e.g., 'received', 'processed'), or None for all
        limit:   max results
    
    Returns:
        List of submission dicts.
    """
    sql = """
        SELECT id, email, name, subject, message, form_data, ip_address, status, created_at
        FROM janina_submissions
    """
    params = []
    
    if status:
        sql += " WHERE status = %s"
        params.append(status)
    
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    try:
        with get_db_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("Failed to get submissions: %s", e)
        return []


# ---------------------------------------------------------------------------
# Stats & Health Check
# ---------------------------------------------------------------------------

def get_janina_stats() -> Dict:
    """
    Comprehensive stats across all Janina tables.
    One call to see everything: responses, feedback, submissions.
    """
    stats = {
        "responses": {
            "total_active": 0,
            "by_category": {},
        },
        "feedback": {
            "total": 0,
            "by_type": {},
            "by_status": {},
        },
        "submissions": {
            "total": 0,
            "by_status": {},
        },
    }
    
    try:
        with get_db_conn() as conn:
            # Response stats
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT category, COUNT(*) as cnt
                    FROM janina_responses
                    WHERE active = TRUE
                    GROUP BY category
                """)
                stats["responses"]["by_category"] = {
                    row["category"]: row["cnt"] for row in cur.fetchall()
                }
                stats["responses"]["total_active"] = sum(
                    stats["responses"]["by_category"].values()
                )
            
            # Feedback stats
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT COUNT(*) as cnt FROM janina_feedback")
                stats["feedback"]["total"] = cur.fetchone()["cnt"]
                
                cur.execute("""
                    SELECT feedback_type, COUNT(*) as cnt
                    FROM janina_feedback
                    GROUP BY feedback_type
                """)
                stats["feedback"]["by_type"] = {
                    row["feedback_type"]: row["cnt"] for row in cur.fetchall()
                }
                
                cur.execute("""
                    SELECT status, COUNT(*) as cnt
                    FROM janina_feedback
                    GROUP BY status
                """)
                stats["feedback"]["by_status"] = {
                    row["status"]: row["cnt"] for row in cur.fetchall()
                }
            
            # Submission stats
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT COUNT(*) as cnt FROM janina_submissions")
                stats["submissions"]["total"] = cur.fetchone()["cnt"]
                
                cur.execute("""
                    SELECT status, COUNT(*) as cnt
                    FROM janina_submissions
                    GROUP BY status
                """)
                stats["submissions"]["by_status"] = {
                    row["status"]: row["cnt"] for row in cur.fetchall()
                }
    
    except Exception as e:
        logger.error("Failed to get Janina stats: %s", e)
    
    return stats
