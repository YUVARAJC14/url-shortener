from datetime import datetime
from app import db
from app.models import Link, Click
from tests.conftest import CREDS

IPHONE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
          "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

def make_link(client, url="https://example.com/page"):
    client.post("/links/create", data={"original_url": url, "expires_in": "0"})

def first_link(app):
    with app.app_context():
        link = Link.query.first()
        return link.id, link.short_code

def test_register_and_login(client):
    r = client.post("/auth/register", follow_redirects=True,
                    data={**CREDS, "confirm": CREDS["password"]})
    assert b"Account created" in r.data
    r = client.post("/auth/login", data=CREDS, follow_redirects=True)
    assert b"Hello" in r.data

def test_dashboard_requires_login(client):
    r = client.get("/dashboard")
    assert r.status_code == 302 and "/auth/login" in r.headers["Location"]

def test_create_link_and_redirect(auth, app):
    make_link(auth)
    _, code = first_link(app)
    r = auth.get(f"/{code}")
    assert r.status_code == 302
    assert r.headers["Location"] == "https://example.com/page"

def test_invalid_url_rejected(auth, app):
    make_link(auth, "javascript:alert(1)")
    with app.app_context():
        assert Link.query.count() == 0

def test_click_is_logged(auth, app):
    make_link(auth)
    _, code = first_link(app)
    auth.get(f"/{code}", headers={"User-Agent": IPHONE})
    with app.app_context():
        click = Click.query.one()
        assert click.device == "Phone"

def test_unknown_code_returns_404(client):
    assert client.get("/nope123").status_code == 404

def test_expired_link_returns_410(auth, app):
    make_link(auth)
    link_id, code = first_link(app)
    with app.app_context():
        db.session.get(Link, link_id).expires_at = datetime(2020, 1, 1)
        db.session.commit()
    assert auth.get(f"/{code}").status_code == 410

def test_cannot_delete_other_users_link(auth, app):
    make_link(auth)
    link_id, _ = first_link(app)
    other = app.test_client()
    creds_b = {"email": "b@test.com", "password": "password123"}
    other.post("/auth/register", data={**creds_b, "confirm": creds_b["password"]})
    other.post("/auth/login", data=creds_b)
    assert other.post(f"/links/{link_id}/delete").status_code == 404
    with app.app_context():
        assert db.session.get(Link, link_id) is not None