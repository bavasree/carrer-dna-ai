import sys
import os

# Add backend directory to Python sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.models import db

env_name = os.getenv('FLASK_ENV', 'production')
app = create_app(env_name)

# Ensure database tables exist if database is connected
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        # Avoid crashing startup if DB is offline or cold-starting
        print(f"[*] Database init check: {e}")

# Entry point for WSGI / local test
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
