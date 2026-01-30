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

    def validate_api_key(self) -> bool:
        """API key'in ayarlanip ayarlanmadigini kontrol eder."""
        return bool(self.openai_api_key and self.openai_api_key != "your-api-key-here")


def get_settings() -> Settings:
    """
    Ayarlari yukler ve dondurur.

    Raises:
        ValidationError: OPENAI_API_KEY eksikse
    """
    return Settings()


__all__ = ["Settings", "get_settings"]
