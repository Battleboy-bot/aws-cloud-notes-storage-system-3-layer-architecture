import logging

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.middleware.exceptions import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return jsonify({"error": error.description}), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        logger.exception("Unhandled application error")
        return jsonify({"error": "Internal server error"}), 500
