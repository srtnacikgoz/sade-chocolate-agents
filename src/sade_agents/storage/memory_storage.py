"""
Sade Agents - In-Memory Storage.

Firebase yapilandirmadiginda kullanilan fallback storage.
Veriler uygulama kapaninca silinir.
"""

from datetime import datetime

from sade_agents.storage.base import BaseStorage, CrewResult


class MemoryStorage(BaseStorage):
    """
    In-memory storage backend.

    Test ve gelistirme ortamlari icin idealdir.
    Veriler kalici degildir.
    """

    def __init__(self) -> None:
        """Storage'i baslatir."""
        # Tenant bazli depolama: {tenant_id: {result_id: CrewResult}}
        self._data: dict[str, dict[str, CrewResult]] = {}

    def _ensure_tenant(self, tenant_id: str) -> None:
        """Tenant bucket'inin var oldugundan emin olur."""
        if tenant_id not in self._data:
            self._data[tenant_id] = {}

    def save(self, result: CrewResult) -> str:
        """Crew sonucunu kaydeder."""
        self._ensure_tenant(result.tenant_id)
        self._data[result.tenant_id][result.result_id] = result
        return result.result_id

    def get(self, result_id: str, tenant_id: str = "default") -> CrewResult | None:
        """ID ile sonuc getirir."""
        self._ensure_tenant(tenant_id)
        return self._data[tenant_id].get(result_id)

    def list_by_tenant(
        self,
        tenant_id: str = "default",
        crew_type: str | None = None,
        include_deleted: bool = False,
        limit: int = 50,
    ) -> list[CrewResult]:
        """Tenant'a ait sonuclari listeler."""
        self._ensure_tenant(tenant_id)

        results = list(self._data[tenant_id].values())

        # Soft delete filtresi
        if not include_deleted:
            results = [r for r in results if not r.is_deleted]

        # Crew type filtresi
        if crew_type:
            results = [r for r in results if r.crew_type == crew_type]

        # Tarihe gore sirala (en yeniden en eskiye)
        results.sort(key=lambda r: r.created_at, reverse=True)

        return results[:limit]

    def soft_delete(self, result_id: str, tenant_id: str = "default") -> bool:
        """Sonucu soft delete yapar."""
        result = self.get(result_id, tenant_id)
        if result is None:
            return False

        result.deleted_at = datetime.utcnow()
        return True

    def clear(self, tenant_id: str | None = None) -> None:
        """
        Tum verileri temizler.

        Args:
            tenant_id: Belirtilirse sadece o tenant temizlenir
        """
        if tenant_id:
            self._data[tenant_id] = {}
        else:
            self._data = {}

    def count(self, tenant_id: str = "default", include_deleted: bool = False) -> int:
        """
        Sonuc sayisini dondurur.

        Args:
            tenant_id: Tenant ID
            include_deleted: Silinmisleri dahil et

        Returns:
            Sonuc sayisi
        """
        self._ensure_tenant(tenant_id)
        results = self._data[tenant_id].values()

        if not include_deleted:
            results = [r for r in results if not r.is_deleted]

        return len(list(results))
