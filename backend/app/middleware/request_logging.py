import logging
import time
import uuid

from flask import Flask, g, request

logger = logging.getLogger(__name__)


def register_request_logging(app: Flask) -> None:
    @app.before_request
    def before_request():
        g.request_id = request.headers.get("X-Amzn-Trace-Id", str(uuid.uuid4()))
        g.start_time = time.perf_counter()

    @app.after_request
    def after_request(response):
        duration_ms = round((time.perf_counter() - g.start_time) * 1000, 2)
        response.headers["X-Request-ID"] = g.request_id
        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%s",
            g.request_id,
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response
