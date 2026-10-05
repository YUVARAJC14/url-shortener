import os
from dotenv import load_dotenv

load_dotenv()

def _db_uri():
    uri = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    # Render gives postgres:// or postgresql://. Name the driver explicitly.
    for prefix in ("postgres://", "postgresql://"):
        if uri.startswith(prefix):
            return "postgresql+psycopg://" + uri[len(prefix):]
    return uri

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = _db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False