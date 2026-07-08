from werkzeug.datastructures import FileStorage

from app.middleware.exceptions import NotFoundError, ValidationError
from app.repository.file_repository import FileRepository
from app.services.storage_service import S3StorageService


class FileService:
    def __init__(self, repository: FileRepository | None = None, storage: S3StorageService | None = None):
        self.repository = repository or FileRepository()
        self.storage = storage or S3StorageService()

    def upload_file(self, title: str, file: FileStorage):
        self._validate_title(title)
        self._validate_file(file)
        filename, s3_key, content_type, size_bytes = self.storage.upload(file)
        metadata = self.repository.create(title, filename, s3_key, content_type, size_bytes)
        return metadata.to_dict()

    def list_files(self, page: int, page_size: int) -> dict:
        page, page_size = self._validate_pagination(page, page_size)
        items, total = self.repository.list(page, page_size)
        return {
            "items": [item.to_dict() for item in items],
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }

    def get_download_url(self, filename: str) -> dict:
        if not filename:
            raise ValidationError("filename is required")
        metadata = self.repository.find_by_filename(filename)
        if not metadata:
            raise NotFoundError("File not found")
        return {"download_url": self.storage.create_download_url(metadata.s3_key), "file": metadata.to_dict()}

    def delete_file(self, file_id: int) -> None:
        metadata = self.repository.find_by_id(file_id)
        if not metadata:
            raise NotFoundError("File not found")
        self.storage.delete(metadata.s3_key)
        self.repository.delete(file_id)

    def search(self, title: str, page: int, page_size: int) -> dict:
        self._validate_title(title)
        page, page_size = self._validate_pagination(page, page_size)
        items, total = self.repository.search_by_title(title, page, page_size)
        return {
            "items": [item.to_dict() for item in items],
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }

    @staticmethod
    def _validate_file(file: FileStorage | None) -> None:
        if not file or not file.filename:
            raise ValidationError("file is required")

    @staticmethod
    def _validate_title(title: str | None) -> None:
        if not title or not title.strip():
            raise ValidationError("title is required")
        if len(title.strip()) > 150:
            raise ValidationError("title must be 150 characters or fewer")

    @staticmethod
    def _validate_pagination(page: int, page_size: int) -> tuple[int, int]:
        if page < 1:
            raise ValidationError("page must be greater than zero")
        if page_size < 1 or page_size > 100:
            raise ValidationError("page_size must be between 1 and 100")
        return page, page_size
