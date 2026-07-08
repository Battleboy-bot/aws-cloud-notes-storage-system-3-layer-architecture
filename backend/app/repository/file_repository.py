from __future__ import annotations

from app.models.file_metadata import FileMetadata
from app.repository.db import get_connection


class FileRepository:
    def create(self, title: str, filename: str, s3_key: str, content_type: str, size_bytes: int) -> FileMetadata:
        query = """
            INSERT INTO files (title, filename, s3_key, content_type, size_bytes)
            VALUES (%s, %s, %s, %s, %s)
        """
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (title, filename, s3_key, content_type, size_bytes))
                file_id = cursor.lastrowid
                cursor.execute("SELECT * FROM files WHERE id = %s", (file_id,))
                return FileMetadata.from_row(cursor.fetchone())

    def list(self, page: int, page_size: int) -> tuple[list[FileMetadata], int]:
        offset = (page - 1) * page_size
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM files")
                total = cursor.fetchone()["total"]
                cursor.execute(
                    """
                    SELECT * FROM files
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (page_size, offset),
                )
                return [FileMetadata.from_row(row) for row in cursor.fetchall()], total

    def find_by_filename(self, filename: str) -> FileMetadata | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM files WHERE filename = %s", (filename,))
                row = cursor.fetchone()
                return FileMetadata.from_row(row) if row else None

    def find_by_id(self, file_id: int) -> FileMetadata | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM files WHERE id = %s", (file_id,))
                row = cursor.fetchone()
                return FileMetadata.from_row(row) if row else None

    def search_by_title(self, title: str, page: int, page_size: int) -> tuple[list[FileMetadata], int]:
        term = f"%{title}%"
        offset = (page - 1) * page_size
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM files WHERE title LIKE %s", (term,))
                total = cursor.fetchone()["total"]
                cursor.execute(
                    """
                    SELECT * FROM files
                    WHERE title LIKE %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (term, page_size, offset),
                )
                return [FileMetadata.from_row(row) for row in cursor.fetchall()], total

    def delete(self, file_id: int) -> bool:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
                return cursor.rowcount > 0
