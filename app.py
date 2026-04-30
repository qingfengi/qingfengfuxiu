from flask import Flask, jsonify, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import logging
from database import init_db, get_articles, get_stats
from scraper import fetch_all
from config import FETCH_INTERVAL, RSS_SOURCES, TWITTER_ACCOUNTS, TWITTER_BEARER_TOKEN

log = logging.getLogger(__name__)
app = Flask(__name__)

_fetch_lock = threading.Lock()


def scheduled_fetch():
    if _fetch_lock.acquire(blocking=False):
        try:
            fetch_all()
        finally:
            _fetch_lock.release()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/articles")
def api_articles():
    limit = min(int(request.args.get("limit", 50)), 200)
    offset = int(request.args.get("offset", 0))
    category = request.args.get("category")
    country = request.args.get("country")
    source_id = request.args.get("source_id")
    keyword = request.args.get("keyword")
    articles = get_articles(
        limit=limit,
        offset=offset,
        category=category,
        country=country,
        source_id=source_id,
        keyword=keyword,
    )
    return jsonify(articles)


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/sources")
def api_sources():
    rss = [
        {
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "country": s["country"],
            "flag": s.get("flag", ""),
            "color": s.get("color", "#666"),
            "type": "rss",
        }
        for s in RSS_SOURCES
    ]
    tw = [
        {
            "id": f"tw_{a['username'].lower()}",
            "name": f"{a['name']} (@{a['username']})",
            "category": a["category"],
            "country": a["country"],
            "flag": a.get("flag", ""),
            "color": "#1DA1F2",
            "type": "twitter",
            "enabled": bool(TWITTER_BEARER_TOKEN),
        }
        for a in TWITTER_ACCOUNTS
    ]
    return jsonify({"rss": rss, "twitter": tw, "twitter_enabled": bool(TWITTER_BEARER_TOKEN)})


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Manually trigger a data refresh."""
    if _fetch_lock.acquire(blocking=False):
        t = threading.Thread(target=lambda: (fetch_all(), _fetch_lock.release()))
        t.daemon = True
        t.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already_running"})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    init_db()

    # Initial fetch on startup
    t = threading.Thread(target=scheduled_fetch, daemon=True)
    t.start()

    # Scheduled fetch
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_fetch, "interval", seconds=FETCH_INTERVAL)
    scheduler.start()

    app.run(host="0.0.0.0", port=5000, debug=False)
