from flask import Blueprint

from app.controllers.file_controller import FileController

files_bp = Blueprint("files", __name__)
controller = FileController()

files_bp.add_url_rule("", view_func=controller.upload, methods=["POST"])
files_bp.add_url_rule("", view_func=controller.list, methods=["GET"])
files_bp.add_url_rule("/search", view_func=controller.search, methods=["GET"])
files_bp.add_url_rule("/<path:filename>", view_func=controller.download, methods=["GET"])
files_bp.add_url_rule("/<int:file_id>", view_func=controller.delete, methods=["DELETE"])
