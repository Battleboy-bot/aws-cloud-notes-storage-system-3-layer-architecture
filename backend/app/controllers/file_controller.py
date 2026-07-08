from flask import jsonify, request

from app.middleware.exceptions import ValidationError
from app.services.file_service import FileService


class FileController:
    def __init__(self, service: FileService | None = None):
        self.service = service or FileService()

    def upload(self):
        title = request.form.get("title", "").strip()
        file = request.files.get("file")
        result = self.service.upload_file(title, file)
        return jsonify(result), 201

    def list(self):
        page = self._int_query("page", 1)
        page_size = self._int_query("page_size", 10)
        return jsonify(self.service.list_files(page, page_size)), 200

    def download(self, filename: str):
        return jsonify(self.service.get_download_url(filename)), 200

    def delete(self, file_id: int):
        self.service.delete_file(file_id)
        return jsonify({"message": "File deleted successfully"}), 200

    def search(self):
        title = request.args.get("title", "").strip()
        page = self._int_query("page", 1)
        page_size = self._int_query("page_size", 10)
        return jsonify(self.service.search(title, page, page_size)), 200

    @staticmethod
    def _int_query(name: str, default: int) -> int:
        raw_value = request.args.get(name, default)
        try:
            return int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"{name} must be an integer") from exc
