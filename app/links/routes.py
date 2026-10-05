from flask import redirect, url_for, flash, abort, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.links import bp
from app.links.forms import LinkForm
from app.models import Link, Click
from app.utils import generate_short_code
from app import db, limiter
from datetime import datetime, timedelta, timezone


@bp.route("/create", methods=["POST"])
@limiter.limit("10 per minute")
@login_required
def create():
    form = LinkForm()
    if form.validate_on_submit():
        days = int(form.expires_in.data)
        expires_at = (datetime.now(timezone.utc).replace(tzinfo=None)
                      + timedelta(days=days)) if days else None
        link = Link(
            user_id=current_user.id,
            original_url=form.original_url.data.strip(),
            short_code=generate_short_code(),
            expires_at=expires_at,
        )
        db.session.add(link)
        db.session.commit()
        flash("Short link created.", "success")
    else:
        for errors in form.errors.values():
            for error in errors:
                flash(error, "danger")
    return redirect(url_for("main.dashboard"))

@bp.route("/<int:link_id>/delete", methods=["POST"])
@login_required
def delete(link_id):
    link = db.session.get(Link, link_id)
    if link is None or link.user_id != current_user.id:
        abort(404)  # don't let users delete other people's links
    db.session.delete(link)
    db.session.commit()
    flash("Link deleted.", "success")
    return redirect(url_for("main.dashboard"))

@bp.route("/<int:link_id>")
@login_required
def stats(link_id):
    link = db.session.get(Link, link_id)
    if link is None or link.user_id != current_user.id:
        abort(404)

    def breakdown(column):
        return (db.session.query(column, func.count(Click.id))
                .filter(Click.link_id == link.id)
                .group_by(column)
                .order_by(func.count(Click.id).desc())
                .all())

    recent = (Click.query.filter_by(link_id=link.id)
              .order_by(Click.clicked_at.desc()).limit(10).all())

    return render_template(
        "stats.html", link=link, total=len(link.clicks), recent=recent,
        devices=breakdown(Click.device),
        browsers=breakdown(Click.browser),
        referrers=breakdown(Click.referrer),
    )

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