"""
RSS + Twitter scraper.
RSS: works immediately, no API key needed.
Twitter: needs TWITTER_BEARER_TOKEN in config.py.
"""
import re
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from database import upsert_article
from config import RSS_SOURCES, TWITTER_ACCOUNTS, TWITTER_BEARER_TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

NS_ATOM = "http://www.w3.org/2005/Atom"
NS_CONTENT = "http://purl.org/rss/1.0/modules/content/"
NS_MEDIA = "http://search.yahoo.com/mrss/"
NS_DC = "http://purl.org/dc/elements/1.1/"


def _strip_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _clean(text: str, max_len=300) -> str:
    return _strip_html(text)[:max_len]


def _parse_date_str(s: str) -> str:
    if not s:
        return datetime.now(timezone.utc).isoformat()
    s = s.strip()
    # ISO 8601
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            d = datetime.strptime(s[:25], fmt[:len(s[:25])])
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            return d.isoformat()
        except Exception:
            pass
    # RFC 2822
    try:
        return parsedate_to_datetime(s).isoformat()
    except Exception:
        pass
    return datetime.now(timezone.utc).isoformat()


def _tag(ns: str, local: str) -> str:
    return f"{{{ns}}}{local}"


def _find_text(el, *tags) -> str:
    for tag in tags:
        child = el.find(tag)
        if child is not None and child.text:
            return child.text.strip()
    return ""


def _parse_rss2(root) -> list[dict]:
    """Parse RSS 2.0 feed."""
    items = []
    channel = root.find("channel")
    if channel is None:
        return items
    for item in channel.findall("item"):
        title = _find_text(item, "title")
        link = _find_text(item, "link")
        if not link:
            # try atom:link
            al = item.find(_tag(NS_ATOM, "link"))
            if al is not None:
                link = al.get("href", "")
        if not title or not link:
            continue
        summary = _clean(
            _find_text(item, "description")
            or _find_text(item, _tag(NS_CONTENT, "encoded"))
        )
        pub = _parse_date_str(
            _find_text(item, "pubDate")
            or _find_text(item, _tag(NS_DC, "date"))
        )
        items.append({"title": title, "url": link, "summary": summary, "published": pub})
    return items


def _parse_atom(root) -> list[dict]:
    """Parse Atom feed."""
    items = []
    for entry in root.findall(_tag(NS_ATOM, "entry")):
        title_el = entry.find(_tag(NS_ATOM, "title"))
        title = (title_el.text or "").strip() if title_el is not None else ""

        link = ""
        for lel in entry.findall(_tag(NS_ATOM, "link")):
            if lel.get("rel", "alternate") == "alternate":
                link = lel.get("href", "")
                break
        if not link:
            lel = entry.find(_tag(NS_ATOM, "link"))
            if lel is not None:
                link = lel.get("href", "")

        if not title or not link:
            continue

        sum_el = entry.find(_tag(NS_ATOM, "summary")) or entry.find(_tag(NS_ATOM, "content"))
        summary = _clean((sum_el.text or "") if sum_el is not None else "")

        pub = _parse_date_str(
            _find_text(entry, _tag(NS_ATOM, "published"))
            or _find_text(entry, _tag(NS_ATOM, "updated"))
        )
        items.append({"title": title, "url": link, "summary": summary, "published": pub})
    return items


def _parse_feed(content: bytes) -> list[dict]:
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        log.warning(f"XML parse error: {e}")
        return []

    tag = root.tag.lower()
    if "rss" in tag or root.tag == "rss":
        return _parse_rss2(root)
    if "feed" in tag or NS_ATOM in root.tag:
        return _parse_atom(root)
    # Try RSS channel directly
    channel = root.find("channel")
    if channel is not None:
        return _parse_rss2(root)
    # Try Atom entries
    entries = root.findall(_tag(NS_ATOM, "entry"))
    if entries:
        return _parse_atom(root)
    return []


def fetch_rss_source(source: dict) -> int:
    """Fetch one RSS source. Returns number of new articles inserted."""
    url = source["url"]
    log.info(f"Fetching RSS: {source['name']} ...")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        log.warning(f"  ✗ {source['name']}: {e}")
        return 0

    items = _parse_feed(resp.content)
    if not items:
        log.warning(f"  ✗ {source['name']}: no items parsed")
        return 0

    count = 0
    for item in items[:30]:
        data = {
            "source_id": source["id"],
            "source_name": source["name"],
            "category": source["category"],
            "country": source["country"],
            "flag": source.get("flag", ""),
            "color": source.get("color", "#666"),
            "title": item["title"],
            "summary": item["summary"],
            "url": item["url"],
            "published": item["published"],
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source_type": "rss",
        }
        if upsert_article(data):
            count += 1

    log.info(f"  ✓ {source['name']}: {count} new")
    return count


def fetch_all_rss() -> int:
    total = 0
    for source in RSS_SOURCES:
        total += fetch_rss_source(source)
    log.info(f"RSS done. Total new: {total}")
    return total


# -------------------------------------------------------
# Twitter API v2 (requires Bearer Token)
# -------------------------------------------------------

def fetch_twitter_user_tweets(account: dict, max_results=10) -> int:
    if not TWITTER_BEARER_TOKEN:
        return 0
    username = account["username"]
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    try:
        r = requests.get(
            f"https://api.twitter.com/2/users/by/username/{username}",
            headers=headers, timeout=10,
        )
        r.raise_for_status()
        user_id = r.json()["data"]["id"]
    except Exception as e:
        log.warning(f"Twitter user lookup failed @{username}: {e}")
        return 0

    try:
        r = requests.get(
            f"https://api.twitter.com/2/users/{user_id}/tweets",
            headers=headers,
            params={"max_results": max_results, "tweet.fields": "created_at,text"},
            timeout=10,
        )
        r.raise_for_status()
        tweets = r.json().get("data", [])
    except Exception as e:
        log.warning(f"Twitter timeline failed @{username}: {e}")
        return 0

    count = 0
    for tw in tweets:
        tweet_id = tw["id"]
        text = tw.get("text", "")
        created = tw.get("created_at", datetime.now(timezone.utc).isoformat())
        data = {
            "source_id": f"tw_{username.lower()}",
            "source_name": f"{account['name']} (@{username})",
            "category": account["category"],
            "country": account["country"],
            "flag": account.get("flag", ""),
            "color": "#1DA1F2",
            "title": text[:200],
            "summary": "",
            "url": f"https://twitter.com/{username}/status/{tweet_id}",
            "published": created,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source_type": "twitter",
        }
        if upsert_article(data):
            count += 1
    log.info(f"Twitter @{username}: {count} new tweets")
    return count


def fetch_all_twitter() -> int:
    if not TWITTER_BEARER_TOKEN:
        log.info("Twitter token not configured, skipping.")
        return 0
    total = sum(fetch_twitter_user_tweets(a) for a in TWITTER_ACCOUNTS)
    log.info(f"Twitter done. Total new: {total}")
    return total


def fetch_all():
    return fetch_all_rss() + fetch_all_twitter()


if __name__ == "__main__":
    from database import init_db
    init_db()
    fetch_all()
