"""
Sade Agents - Design Skills.

Figma MCP server uzerinden tasarim verilerine erisim.
UI Expert Agent bu skill'leri kullanarak Figma'dan veri ceker.
"""

from crewai.tools import tool
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import logging

logger = logging.getLogger(__name__)


class DesignData(BaseModel):
    """Figma'dan cekilen tasarim verisi."""

    frame_name: str = Field(description="Frame adi")
    width: int = Field(description="Frame genisligi (px)")
    height: int = Field(description="Frame yuksekligi (px)")
    background_color: Optional[str] = Field(default=None, description="Arka plan rengi (hex)")

    components: list[Dict[str, Any]] = Field(
        default_factory=list,
        description="Frame icindeki component'lar"
    )

    colors: list[str] = Field(
        default_factory=list,
        description="Kullanilan renkler (hex)"
    )

    typography: Dict[str, Any] = Field(
        default_factory=dict,
        description="Font bilgileri (family, size, weight)"
    )

    spacing: Dict[str, int] = Field(
        default_factory=dict,
        description="Spacing degerleri (padding, margin, gap)"
    )


@tool
def fetch_figma_design(frame_url: str) -> str:
    """
    Figma frame'inden tasarim verisini ceker.

    Figma MCP server'i kullanarak belirtilen frame'in
    layout, renk, tipografi ve component bilgilerini alir.

    Args:
        frame_url: Figma frame URL'si
                   (Orn: https://www.figma.com/file/abc123/Design?node-id=1:2)

    Returns:
        JSON string olarak tasarim verisi:
        - frame_name: Frame adi
        - width, height: Boyutlar
        - components: Icindeki elemanlar
        - colors: Kullanilan renkler
        - typography: Font bilgileri
        - spacing: Bosluk degerleri

    Raises:
        ValueError: Gecersiz URL formati
        RuntimeError: Figma MCP baglanti hatasi

    Example:
        >>> result = fetch_figma_design("https://figma.com/file/xyz/Frame-1")
        >>> data = json.loads(result)
        >>> print(data["frame_name"])
        "Frame-1"

    Note:
        Bu tool, Figma MCP server'in aktif ve auth olmasi gerektirir.
        MCP baglanamiyorsa mock data doner (development icin).
    """
    logger.info(f"Figma tasarim cekiliyor: {frame_url}")

    # URL validation
    if not frame_url or "figma.com" not in frame_url:
        raise ValueError(
            f"Gecersiz Figma URL: {frame_url}. "
            "Format: https://www.figma.com/file/FILE_ID/NAME?node-id=X:Y"
        )

    # TODO: Gercek MCP entegrasyonu
    # Simdilik mock data dondur - MCP entegrasyonu icin:
    # 1. Claude Desktop'ta Figma MCP server configure edilmis olmali
    # 2. mcp__figma-desktop__get-frame-info tool'u cagrilmali

    # Mock design data (development/testing icin)
    mock_data = DesignData(
        frame_name=_extract_frame_name(frame_url),
        width=1200,
        height=800,
        background_color="#FAFAF8",  # Sade krem tonu
        components=[
            {"type": "text", "content": "Baslik", "x": 40, "y": 40, "font_size": 24},
            {"type": "container", "x": 40, "y": 100, "width": 1120, "height": 600},
            {"type": "button", "content": "Kaydet", "x": 40, "y": 720, "variant": "primary"},
        ],
        colors=["#FAFAF8", "#2C2C2C", "#8B7355", "#E8E4DE"],  # Sade paleti
        typography={
            "heading": {"family": "Inter", "size": 24, "weight": 600},
            "body": {"family": "Inter", "size": 16, "weight": 400},
            "caption": {"family": "Inter", "size": 14, "weight": 400},
        },
        spacing={
            "padding": 40,
            "gap": 16,
            "margin": 24,
        },
    )

    logger.info(f"Tasarim verisi alindi: {mock_data.frame_name}")
    return mock_data.model_dump_json()


@tool
def extract_design_tokens(design_json: str) -> str:
    """
    Tasarim verisinden design token'lari cikarir.

    Figma tasarimindan Streamlit kodu uretirken kullanilacak
    renk, tipografi ve spacing degerlerini standart formata donusturur.

    Args:
        design_json: fetch_figma_design'dan donen JSON string

    Returns:
        Design tokens JSON:
        - colors: {"background": "#...", "text": "#...", "accent": "#..."}
        - typography: {"heading_size": 24, "body_size": 16, ...}
        - spacing: {"small": 8, "medium": 16, "large": 24}

    Example:
        >>> design = fetch_figma_design("https://figma.com/...")
        >>> tokens = extract_design_tokens(design)
        >>> print(json.loads(tokens)["colors"]["accent"])
        "#8B7355"
    """
    try:
        data = json.loads(design_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gecersiz JSON: {e}")

    # Extract colors
    colors = data.get("colors", [])
    color_tokens = {
        "background": colors[0] if len(colors) > 0 else "#FFFFFF",
        "text": colors[1] if len(colors) > 1 else "#000000",
        "accent": colors[2] if len(colors) > 2 else "#0066CC",
        "muted": colors[3] if len(colors) > 3 else "#666666",
    }

    # Extract typography
    typography = data.get("typography", {})
    typography_tokens = {
        "heading_size": typography.get("heading", {}).get("size", 24),
        "body_size": typography.get("body", {}).get("size", 16),
        "font_family": typography.get("body", {}).get("family", "Inter"),
    }

    # Extract spacing
    spacing = data.get("spacing", {})
    spacing_tokens = {
        "small": spacing.get("gap", 16) // 2,
        "medium": spacing.get("gap", 16),
        "large": spacing.get("padding", 40),
    }

    tokens = {
        "colors": color_tokens,
        "typography": typography_tokens,
        "spacing": spacing_tokens,
    }

    logger.info("Design tokens cikarildi")
    return json.dumps(tokens, indent=2)


def _extract_frame_name(url: str) -> str:
    """URL'den frame adini cikarir."""
    # https://figma.com/file/xyz/Frame-Name?node-id=1:2
    try:
        # /file/ dan sonraki kisim
        parts = url.split("/")
        if "file" in parts:
            file_idx = parts.index("file")
            if len(parts) > file_idx + 2:
                name = parts[file_idx + 2].split("?")[0]
                return name.replace("-", " ")
    except Exception:
        pass
    return "Untitled Frame"


__all__ = ["fetch_figma_design", "extract_design_tokens", "DesignData"]
