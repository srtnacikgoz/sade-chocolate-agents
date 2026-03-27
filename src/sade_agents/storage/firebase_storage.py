"""
Sade Agents - Firebase/Firestore Storage.

Uretim ortami icin kalici storage backend.
Multi-tenant yapiya uygun Firestore collection yapisi.

Firestore Yapisi:
    tenants/
    └── {tenant_id}/
        └── crew_results/
            └── {result_id}/
                ├── crew_type: str
                ├── inputs: dict
                ├── outputs: dict
                ├── created_at: timestamp
                └── deleted_at: timestamp | null
"""

from datetime import datetime
from typing import Any

from sade_agents.storage.base import BaseStorage, CrewResult


class FirebaseStorage(BaseStorage):
    """
    Firebase/Firestore storage backend.

    Uretim ortami icin kalici depolama saglar.
    Multi-tenant yapiya hazirdir.
    """

    def __init__(self, project_id: str, credentials_path: str) -> None:
        """
        Firebase storage'i baslatir.

        Args:
            project_id: Firebase proje ID'si
            credentials_path: Service account JSON dosya yolu
        """
        self._project_id = project_id
        self._credentials_path = credentials_path
        self._db = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Firebase baglantisinin kuruldugundan emin olur (lazy init)."""
        if self._initialized:
            return

        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            # Firebase app zaten baslatildiysa tekrar baslatma
            try:
                firebase_admin.get_app()
            except ValueError:
                cred = credentials.Certificate(self._credentials_path)
                firebase_admin.initialize_app(cred, {"projectId": self._project_id})

            self._db = firestore.client()
            self._initialized = True
        except ImportError as e:
            raise ImportError(
                "Firebase kullanimi icin 'firebase-admin' ve "
                "'google-cloud-firestore' paketlerini yukleyin: "
                "pip install firebase-admin google-cloud-firestore"
            ) from e

    def _get_collection_ref(self, tenant_id: str) -> Any:
        """Tenant'a ait crew_results collection referansi dondurur."""
        self._ensure_initialized()
        return self._db.collection("tenants").document(tenant_id).collection("crew_results")

    def save(self, result: CrewResult) -> str:
        """Crew sonucunu Firestore'a kaydeder."""
        collection = self._get_collection_ref(result.tenant_id)
        doc_ref = collection.document(result.result_id)
        doc_ref.set(result.to_dict())
        return result.result_id

    def get(self, result_id: str, tenant_id: str = "default") -> CrewResult | None:
        """ID ile sonuc getirir."""
        collection = self._get_collection_ref(tenant_id)
        doc = collection.document(result_id).get()

        if not doc.exists:
            return None

        return CrewResult.from_dict(doc.to_dict())

    def list_by_tenant(
        self,
        tenant_id: str = "default",
        crew_type: str | None = None,
        include_deleted: bool = False,
        limit: int = 50,
    ) -> list[CrewResult]:
        """Tenant'a ait sonuclari listeler."""
        collection = self._get_collection_ref(tenant_id)

        # Tum dokumanlari al (index gerektirmez)
        docs = collection.limit(limit * 2).stream()

        results = []
        for doc in docs:
            result = CrewResult.from_dict(doc.to_dict())

            # Filtrele: crew_type
            if crew_type and result.crew_type != crew_type:
                continue

            # Filtrele: soft delete
            if not include_deleted and result.is_deleted:
                continue

            results.append(result)

            if len(results) >= limit:
                break

        # Tarihe gore sirala (Python'da)
        results.sort(key=lambda r: r.created_at, reverse=True)

        return results

    def soft_delete(self, result_id: str, tenant_id: str = "default") -> bool:
        """Sonucu soft delete yapar."""
        collection = self._get_collection_ref(tenant_id)
        doc_ref = collection.document(result_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        doc_ref.update({"deleted_at": datetime.utcnow().isoformat()})
        return True

    def hard_delete(self, result_id: str, tenant_id: str = "default") -> bool:
        """
        Sonucu kalici olarak siler.

        DİKKAT: Bu islem geri alinamaz!

        Args:
            result_id: Sonuc ID'si
            tenant_id: Tenant ID

        Returns:
            Basarili ise True
        """
        collection = self._get_collection_ref(tenant_id)
        doc_ref = collection.document(result_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        doc_ref.delete()
        return True
