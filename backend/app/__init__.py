import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .models import db
try:
    from config import config_by_name, Config
except ImportError:
    from ..config import config_by_name, Config

# Initialize extensions
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[Config.RATELIMIT_DEFAULT],
    storage_uri=Config.RATELIMIT_STORAGE_URI
)

def create_app(config_name='default'):
    """
    Flask Application Factory.
    Maps template_folder and static_folder directly to sibling frontend/ directories.
    """
    cfg = config_by_name.get(config_name, Config)

    app = Flask(
        __name__,
        template_folder=cfg.TEMPLATE_FOLDER,
        static_folder=cfg.STATIC_FOLDER,
        static_url_path='/static'
    )
    app.config.from_object(cfg)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    limiter.init_app(app)

    # Ensure Uploads Directory Exists
    upload_folder = os.path.join(cfg.STATIC_FOLDER, 'uploads', 'resumes')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

    # Safe Schema Column Synchronization
    with app.app_context():
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                try:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN submitted_details_json TEXT"))
                    conn.commit()
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN resume_filename VARCHAR(255)"))
                    conn.commit()
                except Exception:
                    pass
        except Exception:
            pass

    # JWT Error Callbacks
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "data": {},
            "message": "Token has expired. Please log in again."
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "success": False,
            "data": {},
            "message": f"Invalid token: {error}"
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "success": False,
            "data": {},
            "message": "Authentication token is missing. Please log in."
        }), 401

    # Centralized HTTP Error Handlers
    def register_error_handlers(flask_app):
        @flask_app.errorhandler(400)
        def bad_request_error(e):
            return jsonify({
                "success": False,
                "data": {},
                "message": getattr(e, 'description', 'Bad Request')
            }), 400

        @flask_app.errorhandler(401)
        def unauthorized_error(e):
            return jsonify({
                "success": False,
                "data": {},
                "message": getattr(e, 'description', 'Unauthorized')
            }), 401

        @flask_app.errorhandler(403)
        def forbidden_error(e):
            return jsonify({
                "success": False,
                "data": {},
                "message": getattr(e, 'description', 'Access forbidden')
            }), 403

        @flask_app.errorhandler(404)
        def not_found_error(e):
            if request.path.startswith('/api/'):
                return jsonify({
                    "success": False,
                    "data": {},
                    "message": "The requested API endpoint was not found."
                }), 404
            # Serve index for frontend routing fallback if not a static file
            return jsonify({
                "success": False,
                "data": {},
                "message": "Resource not found"
            }), 404

        @flask_app.errorhandler(429)
        def ratelimit_handler(e):
            return jsonify({
                "success": False,
                "data": {},
                "message": f"Rate limit exceeded: {e.description}"
            }), 429

        @flask_app.errorhandler(500)
        def internal_server_error(e):
            return jsonify({
                "success": False,
                "data": {},
                "message": "An internal server error occurred. Please try again."
            }), 500

    register_error_handlers(app)

    # Register Blueprints
    from .routes import (
        auth_bp,
        profile_bp,
        analysis_bp,
        recommendation_bp,
        roadmap_bp,
        resume_bp,
        application_bp,
        admin_bp,
        view_bp
    )

    app.register_blueprint(view_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(application_bp)
    app.register_blueprint(admin_bp)

    return app
