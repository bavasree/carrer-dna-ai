import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env ONLY when NOT running on Vercel.
# On Vercel, env vars are injected directly; loading a stale .env would override them.
basedir = os.path.abspath(os.path.dirname(__file__))
if not os.getenv('VERCEL') and not os.getenv('VERCEL_ENV'):
    load_dotenv(os.path.join(basedir, '.env'), override=True)

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'oppora-fallback-secret-key-2025')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'oppora-fallback-jwt-secret-key-2025')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400)))
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_COOKIE_CSRF_PROTECT = False
    
    # Database Configuration
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'career_dna_ai')
    
    # Default to MySQL via PyMySQL
    default_mysql_uri = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    raw_db_url = os.getenv('DATABASE_URL')
    if raw_db_url:
        if raw_db_url.startswith('postgres://'):
            raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)
        elif raw_db_url.startswith('mysql://') and not raw_db_url.startswith('mysql+pymysql://'):
            raw_db_url = raw_db_url.replace('mysql://', 'mysql+pymysql://', 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        SQLALCHEMY_DATABASE_URI = default_mysql_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Engine Options & SSL handling for Cloud DBs (TiDB, Aiven, etc.)
    engine_options = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }
    if "tidbcloud.com" in SQLALCHEMY_DATABASE_URI or "ssl" in SQLALCHEMY_DATABASE_URI:
        import ssl
        engine_options["connect_args"] = {
            "ssl": ssl.create_default_context()
        }
    SQLALCHEMY_ENGINE_OPTIONS = engine_options
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Rate Limiting
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200 per hour')
    RATELIMIT_AI = os.getenv('RATELIMIT_AI', '60 per minute')
    RATELIMIT_STORAGE_URI = "memory://"
    
    # Frontend directory paths
    FRONTEND_DIR = os.path.abspath(os.path.join(basedir, '..', 'frontend'))
    TEMPLATE_FOLDER = os.path.join(FRONTEND_DIR, 'templates')
    STATIC_FOLDER = os.path.join(FRONTEND_DIR, 'static')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
