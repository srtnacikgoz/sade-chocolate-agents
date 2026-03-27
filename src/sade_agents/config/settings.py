"""
Sade Agents - Yapilandirma ayarlari.

pydantic-settings ile type-safe config yonetimi.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Uygulama ayarlari.

    Ortam degiskenlerinden veya .env dosyasindan yukler.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenAI API (CrewAI icin gerekli)
    openai_api_key: str

    # Opsiyonel: Model secimi
    openai_model_name: str = "gpt-4o-mini"

    # Firebase / Firestore
    firebase_project_id: str | None = None
    firebase_credentials_path: str | None = None

    # Feature Flags (ozellik acma/kapama)
    feature_real_scraping: bool = False
    feature_firebase_storage: bool = False

    # Scraping
    scraping_timeout_seconds: int = 30
    scraping_targets_file: str = "scraping_targets.json"  # Hedefler bu dosyadan okunur

    # Tenant (multi-tenant SaaS hazirlik)
    app_default_tenant_id: str = "default"

    # Reddit API (Growth Hacker icin)
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_user_agent: str = "SadeAgents/1.0 (by /u/sadechocolate)"

    def is_reddit_configured(self) -> bool:
        """Reddit API yapilandirmasinin tamamlanip tamamlanmadigini kontrol eder."""
        return bool(self.reddit_client_id and self.reddit_client_secret)

    def validate_api_key(self) -> bool:
        """API key'in ayarlanip ayarlanmadigini kontrol eder."""
        return bool(self.openai_api_key and self.openai_api_key != "your-api-key-here")

    def is_firebase_configured(self) -> bool:
        """Firebase yapilandirmasinin tamamlanip tamamlanmadigini kontrol eder."""
        return bool(
            self.feature_firebase_storage
            and self.firebase_project_id
            and self.firebase_credentials_path
        )


def get_settings() -> Settings:
    """
    Ayarlari yukler ve dondurur.

    Raises:
        ValidationError: OPENAI_API_KEY eksikse
    """
    return Settings()


__all__ = ["Settings", "get_settings"]
