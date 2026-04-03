from flask import Flask
from app.config import get_config
from app.extensions import db, migrate, jwt, bcrypt


def create_app():
    """Application factory — creates and wires up the Flask app."""
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.transactions import transactions_bp
    from app.routes.analytics import analytics_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(transactions_bp, url_prefix="/transactions")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(users_bp, url_prefix="/users")

    # Health check
    @app.route("/health")
    def health():
        return {"status": "ok", "message": "FinTrack API is running"}, 200

    # Global Error Handlers
    from app.utils.responses import error
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return error(message=e.description, status=e.code)

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        # In production this should be logged to a file/APM
        return error(message="An unexpected server error occurred.", status=500)

    return app
