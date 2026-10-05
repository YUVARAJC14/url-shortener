from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    links = db.relationship("Link", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    original_url = db.Column(db.Text, nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    clicks = db.relationship("Click", backref="link", lazy=True,
                             cascade="all, delete-orphan")


class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey("link.id"), nullable=False, index=True)
    clicked_at = db.Column(db.DateTime, default=utcnow, index=True)
    browser = db.Column(db.String(50))
    device = db.Column(db.String(30))
    referrer = db.Column(db.String(255))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))