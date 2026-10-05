import os
from dotenv import load_dotenv

load_dotenv()

def _db_uri():
    uri = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    if uri.startswith("postgres://"):  # some hosts still use the old prefix
        uri = uri.replace("postgres://", "postgresql://", 1)
    return uri

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = _db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False