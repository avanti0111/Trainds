from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=Config.CORS_ORIGINS)

    # Database Initialization
    from app.db import init_db
    try:
        init_db()
    except Exception as e:
        print("Database intialization error:", e)

    # Import blueprints
    from app.routes.route_engine import bp as route_bp
    from app.routes.delay import bp as delay_bp
    from app.routes.live_train import bp as live_bp
    from app.routes.megablock import bp as mega_bp
    from app.routes.weather import bp as weather_bp
    from app.routes.chat import bp as chat_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.feedback import bp as feedback_bp

    # Register blueprints with /api prefix
    app.register_blueprint(route_bp, url_prefix="/api")
    app.register_blueprint(delay_bp, url_prefix="/api")
    app.register_blueprint(live_bp, url_prefix="/api")
    app.register_blueprint(mega_bp, url_prefix="/api")
    app.register_blueprint(weather_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")

    @app.route("/health")
    def health():
        return {"status": "ok", "service": "TRAiNDS API"}

    return app