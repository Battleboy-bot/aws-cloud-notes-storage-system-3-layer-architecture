import logging
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.config.settings import get_settings
from app.middleware.exceptions import StorageError

logger = logging.getLogger(__name__)


class S3StorageService:
    def __init__(self):
        self.settings = get_settings()
        self.client = boto3.client("s3", region_name=self.settings.aws_region)

    def upload(self, file: FileStorage) -> tuple[str, str, str, int]:
        safe_name = secure_filename(file.filename or "")
        extension = safe_name.rsplit(".", 1)[-1] if "." in safe_name else "bin"
        object_key = f"notes/{uuid4()}.{extension}"
        content_type = file.mimetype or "application/octet-stream"

        file.stream.seek(0, 2)
        size_bytes = file.stream.tell()
        file.stream.seek(0)

        try:
            self.client.upload_fileobj(
                file,
                self.settings.s3_bucket_name,
                object_key,
                ExtraArgs={"ContentType": content_type, "ServerSideEncryption": "AES256"},
            )
        except (BotoCoreError, ClientError) as exc:
            logger.exception("S3 upload failed")
            raise StorageError("Unable to upload file") from exc

        return safe_name, object_key, content_type, size_bytes

    def create_download_url(self, object_key: str) -> str:
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.settings.s3_bucket_name, "Key": object_key},
                ExpiresIn=self.settings.presigned_url_expiry_seconds,
            )
        except (BotoCoreError, ClientError) as exc:
            logger.exception("S3 presigned URL generation failed")
            raise StorageError("Unable to create download URL") from exc

    def delete(self, object_key: str) -> None:
        try:
            self.client.delete_object(Bucket=self.settings.s3_bucket_name, Key=object_key)
        except (BotoCoreError, ClientError) as exc:
            logger.exception("S3 delete failed")
            raise StorageError("Unable to delete file") from exc
