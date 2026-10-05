import secrets
import string
from app import db
from app.models import Link
from urllib.parse import urlparse
from user_agents import parse

ALPHABET = string.ascii_letters + string.digits  # 62 characters

def generate_short_code(length=6):
    for _ in range(10):  # retry if the code is already taken
        code = "".join(secrets.choice(ALPHABET) for _ in range(length))
        taken = db.session.query(Link.id).filter_by(short_code=code).first()
        if not taken:
            return code
    raise RuntimeError("Could not generate a unique short code")

def parse_click(request):
    ua = parse(request.headers.get("User-Agent", ""))
    if ua.is_bot:
        device = "Bot"
    elif ua.is_tablet:
        device = "Tablet"
    elif ua.is_mobile:
        device = "Phone"
    elif ua.is_pc:
        device = "Computer"
    else:
        device = "Other"

    browser = ua.browser.family or "Unknown"
    referrer = urlparse(request.referrer).netloc if request.referrer else "Direct"
    return browser[:50], device, referrer[:255]