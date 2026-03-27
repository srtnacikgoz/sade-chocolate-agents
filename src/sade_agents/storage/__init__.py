"""
Sade Agents - Storage modulu.

Crew sonuclarini saklamak icin storage backend'leri.
Firebase/Firestore ve in-memory fallback destegi.
"""

from sade_agents.storage.base import BaseStorage, CrewResult
from sade_agents.storage.memory_storage import MemoryStorage

__all__ = ["BaseStorage", "CrewResult", "MemoryStorage", "get_storage"]


def get_storage() -> BaseStorage:
    """
    Yapilandirmaya gore uygun storage backend'i dondurur.

    Firebase yapilandirildiyse FirebaseStorage, degilse MemoryStorage kullanilir.
    """
    from sade_agents.config import get_settings

    settings = get_settings()

    if settings.is_firebase_configured():
        from sade_agents.storage.firebase_storage import FirebaseStorage

        return FirebaseStorage(
            project_id=settings.firebase_project_id,
            credentials_path=settings.firebase_credentials_path,
        )

    return MemoryStorage()
