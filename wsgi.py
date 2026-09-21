import sys
import os

# Add backend directory to Python sys.path since wsgi.py is in the root
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# On Vercel, force the correct cloud database URL BEFORE importing the app.
# This ensures the DATABASE_URL is always set correctly regardless of .env files.
if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
    _db_url = os.getenv('DATABASE_URL', '')
    # Only override if not already a valid cloud DB URL
    if not _db_url or '127.0.0.1' in _db_url or 'localhost' in _db_url or 'example.com' in _db_url:
        os.environ['DATABASE_URL'] = 'mysql+pymysql://2Nywz7ysk5bToPm.root:hvsXjzwKOXS2lQSM@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test'

from app import create_app
from app.models import db

env_name = os.getenv('FLASK_ENV', 'production')
app = create_app(env_name)

@app.route('/healthz')
def healthz():
    """Debug endpoint: shows which DB host is configured (masked credentials)."""
    import re
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')
    # Mask password for security
    masked = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', db_url)
    vercel = os.getenv('VERCEL', 'not-set')
    vercel_env = os.getenv('VERCEL_ENV', 'not-set')
    raw_db_env = os.getenv('DATABASE_URL', 'not-set')
    masked_raw = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', raw_db_env) if raw_db_env else 'not-set'
    from flask import jsonify
    return jsonify({
        "status": "ok",
        "db_url": masked,
        "raw_DATABASE_URL": masked_raw,
        "VERCEL": vercel,
        "VERCEL_ENV": vercel_env
    })

# Entry point for WSGI / local test
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
