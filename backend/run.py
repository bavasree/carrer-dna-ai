import os
from app import create_app
from app.models import db

env_name = os.getenv('FLASK_ENV', 'development')
app = create_app(env_name)

# Ensure database tables exist on startup
with app.app_context():
    try:
        db.create_all()
        print("[*] Database tables verified/initialized.")
    except Exception as e:
        print(f"Note: Database auto-initialization check: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')
    debug = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
    print(f"[*] Career DNA AI starting on http://{host}:{port} in {env_name} mode...")
    app.run(host=host, port=port, debug=debug)
