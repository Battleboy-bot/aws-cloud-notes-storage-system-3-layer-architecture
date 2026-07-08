from flask import Flask
from flask_cors import CORS

from app.config.settings import get_settings
from app.middleware.error_handler import register_error_handlers
from app.middleware.request_logging import register_request_logging
from app.routes.file_routes import files_bp
from app.utils.logging_config import configure_logging


def create_app() -> Flask:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = settings.max_upload_mb * 1024 * 1024

    CORS(app, resources={r"/api/v1/*": {"origins": settings.allowed_origins}})

    register_request_logging(app)
    register_error_handlers(app)

    app.register_blueprint(files_bp, url_prefix="/api/v1/files")

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "aws-cloud-notes-api"}, 200

    return app
