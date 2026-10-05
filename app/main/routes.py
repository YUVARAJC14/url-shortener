from flask import render_template, redirect, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.main import bp
from app.models import Link, Click
from app.links.forms import LinkForm
from app.utils import parse_click
from app.analytics import clicks_per_day, top_links, device_breakdown
from datetime import datetime, timezone
from flask import render_template, redirect, request, abort

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/dashboard")
@login_required
def dashboard():
    days = request.args.get("days", 7, type=int)
    if days not in (7, 30):
        days = 7

    links = (Link.query.filter_by(user_id=current_user.id)
             .order_by(Link.created_at.desc()).all())

    devices = device_breakdown(current_user.id)
    top_device = devices["labels"][0] if devices["labels"] else "None yet"

    charts = {
        "perDay": clicks_per_day(current_user.id, days),
        "devices": devices,
        "topLinks": top_links(current_user.id),
    }
    return render_template("dashboard.html", links=links, form=LinkForm(),
                           top_device=top_device, charts=charts, days=days)
@bp.route("/<short_code>")
def follow(short_code):
    link = Link.query.filter_by(short_code=short_code).first_or_404()
    if link.expires_at and link.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        abort(410)  # 410 Gone: it existed, but is no longer available
    browser, device, referrer = parse_click(request)
    db.session.add(Click(link_id=link.id, browser=browser,
                         device=device, referrer=referrer))
    db.session.commit()
    return redirect(link.original_url, code=302)