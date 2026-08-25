from .auth_routes import auth_bp
from .profile_routes import profile_bp
from .analysis_routes import analysis_bp
from .recommendation_routes import recommendation_bp
from .roadmap_routes import roadmap_bp
from .resume_routes import resume_bp
from .application_routes import application_bp
from .admin_routes import admin_bp
from .view_routes import view_bp

__all__ = [
    'auth_bp',
    'profile_bp',
    'analysis_bp',
    'recommendation_bp',
    'roadmap_bp',
    'resume_bp',
    'application_bp',
    'admin_bp',
    'view_bp'
]
