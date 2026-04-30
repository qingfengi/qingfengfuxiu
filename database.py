import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "media_monitor.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id   TEXT NOT NULL,
            source_name TEXT NOT NULL,
            category    TEXT NOT NULL,
            country     TEXT NOT NULL,
            flag        TEXT DEFAULT '',
            color       TEXT DEFAULT '#666',
            title       TEXT NOT NULL,
            summary     TEXT DEFAULT '',
            url         TEXT UNIQUE NOT NULL,
            published   TEXT NOT NULL,
            fetched_at  TEXT NOT NULL,
            source_type TEXT DEFAULT 'rss'
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_published ON articles(published DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON articles(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_country ON articles(country)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_source_id ON articles(source_id)")
    conn.commit()
    conn.close()


def upsert_article(data: dict) -> bool:
    """Insert article, skip if URL already exists. Returns True if inserted."""
    conn = get_conn()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO articles
                (source_id, source_name, category, country, flag, color,
                 title, summary, url, published, fetched_at, source_type)
            VALUES
                (:source_id, :source_name, :category, :country, :flag, :color,
                 :title, :summary, :url, :published, :fetched_at, :source_type)
        """, data)
        inserted = conn.execute("SELECT changes()").fetchone()[0]
        conn.commit()
        return inserted > 0
    finally:
        conn.close()


def get_articles(limit=100, offset=0, category=None, country=None,
                 source_id=None, keyword=None):
    conn = get_conn()
    conditions = []
    params = []

    if category and category != "全部":
        conditions.append("category = ?")
        params.append(category)
    if country and country != "全部":
        conditions.append("country = ?")
        params.append(country)
    if source_id:
        conditions.append("source_id = ?")
        params.append(source_id)
    if keyword:
        conditions.append("(title LIKE ? OR summary LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = f"SELECT * FROM articles {where} ORDER BY published DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    by_category = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM articles GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    by_country = conn.execute(
        "SELECT country, COUNT(*) as cnt FROM articles GROUP BY country ORDER BY cnt DESC"
    ).fetchall()
    by_source = conn.execute(
        "SELECT source_id, source_name, COUNT(*) as cnt, MAX(published) as latest "
        "FROM articles GROUP BY source_id ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "by_category": [dict(r) for r in by_category],
        "by_country": [dict(r) for r in by_country],
        "by_source": [dict(r) for r in by_source],
    }
