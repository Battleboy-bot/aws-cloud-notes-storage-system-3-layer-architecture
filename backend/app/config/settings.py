import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import boto3


@dataclass(frozen=True)
class Settings:
    aws_region: str
    s3_bucket_name: str
    secret_id: str | None
    parameter_prefix: str | None
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_ssl: bool
    allowed_origins: list[str]
    max_upload_mb: int
    log_level: str
    presigned_url_expiry_seconds: int


def _get_secret(secret_id: str, region_name: str) -> dict[str, Any]:
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_id)
    return json.loads(response["SecretString"])


def _get_parameter(name: str, region_name: str, decrypt: bool = True) -> str:
    client = boto3.client("ssm", region_name=region_name)
    response = client.get_parameter(Name=name, WithDecryption=decrypt)
    return response["Parameter"]["Value"]


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    region = os.getenv("AWS_REGION", "ap-south-1")
    secret_id = os.getenv("DB_SECRET_ID")
    parameter_prefix = os.getenv("PARAMETER_PREFIX")

    secret_values: dict[str, Any] = {}
    if secret_id:
        secret_values = _get_secret(secret_id, region)

    def value(key: str, default: str = "") -> str:
        if key in secret_values:
            return str(secret_values[key])
        if parameter_prefix:
            parameter_name = f"{parameter_prefix.rstrip('/')}/{key}"
            return _get_parameter(parameter_name, region)
        return os.getenv(key, default)

    return Settings(
        aws_region=region,
        s3_bucket_name=os.getenv("S3_BUCKET_NAME") or value("S3_BUCKET_NAME"),
        secret_id=secret_id,
        parameter_prefix=parameter_prefix,
        db_host=value("DB_HOST", "localhost"),
        db_port=int(value("DB_PORT", "3306")),
        db_name=value("DB_NAME", "notes_db"),
        db_user=value("DB_USER", "notes_user"),
        db_password=value("DB_PASSWORD", ""),
        db_ssl=value("DB_SSL", "true").lower() == "true",
        allowed_origins=_split_csv(os.getenv("ALLOWED_ORIGINS", "*")),
        max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "25")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        presigned_url_expiry_seconds=int(os.getenv("PRESIGNED_URL_EXPIRY_SECONDS", "300")),
    )
