"""Abstraction de stockage objet (local en dev, S3 en production)."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path


class ObjectStore(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        """Stocke un objet et retourne sa clé."""

    @abstractmethod
    def get(self, key: str) -> bytes:
        """Récupère le contenu d'un objet."""

    @abstractmethod
    def exists(self, key: str) -> bool: ...


class LocalObjectStore(ObjectStore):
    """Stockage sur disque pour le développement et les tests."""

    def __init__(self, root: str | os.PathLike[str] = "storage") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        self._path(key).write_bytes(data)
        return key

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path(key).exists()


class S3ObjectStore(ObjectStore):
    """Stockage S3 (production). Le client boto3 est importé paresseusement."""

    def __init__(self, bucket: str, **client_kwargs: object) -> None:
        import boto3  # noqa: PLC0415 - import paresseux optionnel

        self.bucket = bucket
        self._client = boto3.client("s3", **client_kwargs)  # type: ignore[arg-type]

    def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        extra = {"ContentType": content_type} if content_type else {}
        self._client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)
        return key

    def get(self, key: str) -> bytes:
        return self._client.get_object(Bucket=self.bucket, Key=key)["Body"].read()

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False


def get_object_store() -> ObjectStore:
    """Sélectionne le backend selon la configuration d'environnement."""
    bucket = os.getenv("S3_BUCKET")
    if bucket and os.getenv("S3_ACCESS_KEY_ID"):
        return S3ObjectStore(
            bucket,
            endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,
            aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
            region_name=os.getenv("S3_REGION") or None,
        )
    return LocalObjectStore(os.getenv("LOCAL_STORAGE_ROOT", "storage"))
