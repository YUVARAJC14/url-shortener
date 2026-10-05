from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from app import db

def clicks_per_day(user_id, days=7):
    since = (datetime.now(timezone.utc) - timedelta(days=days - 1)).date()
    rows = db.session.execute(text("""
        SELECT date(c.clicked_at) AS day, COUNT(*) AS clicks
        FROM click c
        JOIN link l ON l.id = c.link_id
        WHERE l.user_id = :uid AND c.clicked_at >= :since
        GROUP BY day
        ORDER BY day
    """), {"uid": user_id, "since": since.isoformat()}).all()

    counts = {r.day: r.clicks for r in rows}
    labels, values = [], []
    for i in range(days):  # fill days with no clicks with 0
        d = since + timedelta(days=i)
        labels.append(d.strftime("%d %b"))
        values.append(counts.get(d.isoformat(), 0))
    return {"labels": labels, "values": values}

def top_links(user_id, limit=5):
    rows = db.session.execute(text("""
        SELECT l.short_code, COUNT(c.id) AS clicks
        FROM link l
        LEFT JOIN click c ON c.link_id = l.id
        WHERE l.user_id = :uid
        GROUP BY l.id, l.short_code
        ORDER BY clicks DESC, l.created_at DESC
        LIMIT :limit
    """), {"uid": user_id, "limit": limit}).all()
    return {"labels": [r.short_code for r in rows],
            "values": [r.clicks for r in rows]}

def device_breakdown(user_id):
    rows = db.session.execute(text("""
        SELECT c.device, COUNT(*) AS clicks
        FROM click c
        JOIN link l ON l.id = c.link_id
        WHERE l.user_id = :uid
        GROUP BY c.device
        ORDER BY clicks DESC
    """), {"uid": user_id}).all()
    return {"labels": [r.device for r in rows],
            "values": [r.clicks for r in rows]}