"""
Sade Agents - Storage Base Interface.

Tum storage backend'lerinin uymasi gereken temel arayuz.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class CrewResult:
    """Crew calisma sonucu modeli."""

    crew_type: str  # "product_launch" | "market_analysis" | "quality_audit"
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    tenant_id: str = "default"
    result_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None  # Soft delete icin

    def to_dict(self) -> dict[str, Any]:
        """Firestore-uyumlu dict'e donusturur."""
        return {
            "result_id": self.result_id,
            "crew_type": self.crew_type,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "tenant_id": self.tenant_id,
            "created_at": self.created_at.isoformat(),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CrewResult":
        """Dict'ten CrewResult olusturur."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()

        deleted_at = data.get("deleted_at")
        if isinstance(deleted_at, str):
            deleted_at = datetime.fromisoformat(deleted_at)

        return cls(
            result_id=data.get("result_id", str(uuid4())),
            crew_type=data["crew_type"],
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            tenant_id=data.get("tenant_id", "default"),
            created_at=created_at,
            deleted_at=deleted_at,
        )

    @property
    def is_deleted(self) -> bool:
        """Soft delete durumunu kontrol eder."""
        return self.deleted_at is not None


class BaseStorage(ABC):
    """Storage backend'leri icin temel arayuz."""

    @abstractmethod
    def save(self, result: CrewResult) -> str:
        """
        Crew sonucunu kaydeder.

        Args:
            result: Kaydedilecek CrewResult

        Returns:
            Kaydedilen sonucun ID'si
        """
        pass

    @abstractmethod
    def get(self, result_id: str, tenant_id: str = "default") -> CrewResult | None:
        """
        ID ile sonuc getirir.

        Args:
            result_id: Sonuc ID'si
            tenant_id: Tenant ID

        Returns:
            CrewResult veya None (bulunamazsa)
        """
        pass

    @abstractmethod
    def list_by_tenant(
        self,
        tenant_id: str = "default",
        crew_type: str | None = None,
        include_deleted: bool = False,
        limit: int = 50,
    ) -> list[CrewResult]:
        """
        Tenant'a ait sonuclari listeler.

        Args:
            tenant_id: Tenant ID
            crew_type: Opsiyonel crew tipi filtresi
            include_deleted: Silinmisleri dahil et
            limit: Maksimum sonuc sayisi

        Returns:
            CrewResult listesi
        """
        pass

    @abstractmethod
    def soft_delete(self, result_id: str, tenant_id: str = "default") -> bool:
        """
        Sonucu soft delete yapar.

        Args:
            result_id: Sonuc ID'si
            tenant_id: Tenant ID

        Returns:
            Basarili ise True
        """
        pass

    def create_result(
        self,
        crew_type: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        tenant_id: str = "default",
    ) -> CrewResult:
        """
        Yeni CrewResult olusturur ve kaydeder.

        Args:
            crew_type: Crew tipi
            inputs: Giris parametreleri
            outputs: Cikis sonuclari
            tenant_id: Tenant ID

        Returns:
            Kaydedilen CrewResult
        """
        result = CrewResult(
            crew_type=crew_type,
            inputs=inputs,
            outputs=outputs,
            tenant_id=tenant_id,
        )
        self.save(result)
        return result
