import pytest
from app import create_app, db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    SECRET_KEY = "test"

CREDS = {"email": "a@test.com", "password": "password123"}

@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth(client):
    client.post("/auth/register", data={**CREDS, "confirm": CREDS["password"]})
    client.post("/auth/login", data=CREDS)
    return client