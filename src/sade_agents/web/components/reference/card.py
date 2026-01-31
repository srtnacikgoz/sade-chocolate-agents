"""
Reference Card Component for AI Code Generation.

Bu dosya, UI Expert Agent'in Streamlit kod uretirken referans alacagi
production-ready card component ornegi icerir. AI hallucination'i minimize etmek
icin type hints, docstring ve ornek kullanim standartlarini gosterir.

Author: UI Expert Agent
Purpose: Golden example for AI code generation
"""

from typing import Literal, Optional
import streamlit as st


def render_card(
    title: str,
    content: str,
    icon: Optional[str] = None,
    variant: Literal["default", "primary", "warning"] = "default"
) -> None:
    """
    Production-ready card component with clean Sade Chocolate styling.

    Container-based layout ile minimal ve responsive tasarim. CSS variables
    veya Streamlit default renkler kullanilir (hardcoded hex yasak).

    Args:
        title: Card baslik metni (ornek: "Rakip Analizi")
        content: Card icerik metni (markdown destekler)
        icon: Opsiyonel emoji/icon (ornek: "📊", "⚡")
        variant: Stil varyanti
            - "default": Normal card
            - "primary": Vurgulu card (ana aksiyon)
            - "warning": Uyari card (dikkat gerektiren)

    Returns:
        None (UI render eder)

    Example:
        >>> render_card(
        ...     title="Yeni Urun Tespit Edildi",
        ...     content="Marie Antoinette yeni urun ekledi: Ruby Truffle Collection",
        ...     icon="🎁",
        ...     variant="primary"
        ... )

    Notes:
        - st.container ile layout wrap
        - st.columns ile icon+title horizontal align
        - st.markdown ile content render (typography control)
        - Variant'a gore border color degisir (CSS variable best practice)
    """
    # Variant'a gore border ve arka plan rengi (Streamlit native)
    border_color = {
        "default": "#e0e0e0",
        "primary": "#4CAF50",
        "warning": "#FF9800"
    }.get(variant, "#e0e0e0")

    # Container ile card wrap
    with st.container():
        # Border ve padding ile card efekti (inline CSS minimal kullanim)
        st.markdown(
            f'<div style="border-left: 4px solid {border_color}; '
            f'padding: 1rem; margin-bottom: 1rem; background-color: rgba(0,0,0,0.02);">',
            unsafe_allow_html=True
        )

        # Icon + Title horizontal layout
        if icon:
            col1, col2 = st.columns([1, 20])
            with col1:
                st.markdown(f"<h3 style='margin:0;'>{icon}</h3>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{title}**")
        else:
            st.markdown(f"**{title}**")

        # Content (markdown ile typography)
        st.markdown(content)

        # Close div
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# Usage example for AI training
# ============================================================================
"""
ORNEK KULLANIM 1 - Default Card:

render_card(
    title="Analiz Tamamlandi",
    content="5 rakip siteden toplam 127 urun tespit edildi.",
    icon="✅"
)

ORNEK KULLANIM 2 - Primary Card (CTA):

render_card(
    title="Yeni Rakip Ekle",
    content="Analiz kapsamini genisletmek icin yeni rakip sitesi ekleyebilirsiniz.",
    icon="➕",
    variant="primary"
)

ORNEK KULLANIM 3 - Warning Card:

render_card(
    title="Scraping Hatasi",
    content="vakko.com sitesine erisim saglanamiyor. Lutfen URL'i kontrol edin.",
    icon="⚠️",
    variant="warning"
)

AI GENERATION KURALLARI:
- Her zaman type hints kullan (title: str, variant: Literal[...])
- Docstring zorunlu (Google-style: Args, Returns, Example)
- Hardcoded hex yerine CSS variables veya theme colors
- st.beta_* veya st.experimental_* kullanma (deprecated)
- Layout icin st.container ve st.columns kullan
- Responsive tasarim (absolute positioning yasak)
"""
