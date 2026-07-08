from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FileMetadata:
    id: int
    title: str
    filename: str
    s3_key: str
    content_type: str
    size_bytes: int
    created_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "FileMetadata":
        return cls(
            id=row["id"],
            title=row["title"],
            filename=row["filename"],
            s3_key=row["s3_key"],
            content_type=row["content_type"],
            size_bytes=row["size_bytes"],
            created_at=row["created_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "filename": self.filename,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at.isoformat(),
        }
