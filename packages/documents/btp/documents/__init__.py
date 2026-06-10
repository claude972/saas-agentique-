"""Gestion documentaire — stockage, classement, OCR, versioning.

L'abstraction de stockage (`ObjectStore`) permet de basculer entre un backend
local (dev/tests) et S3 (production) sans changer le code appelant.
"""

from __future__ import annotations

from btp.documents.storage import LocalObjectStore, ObjectStore, S3ObjectStore, get_object_store

__all__ = ["ObjectStore", "LocalObjectStore", "S3ObjectStore", "get_object_store"]
