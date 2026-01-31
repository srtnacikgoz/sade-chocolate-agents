"""
Sade Agents - Sidebar Component.

Sol menude navigasyon ve ayarlar.
"""

import streamlit as st


def render_sidebar() -> str:
    """
    Sidebar'i render eder ve secilen sayfayi dondurur.

    Returns:
        Secilen sayfa ID'si
    """
    with st.sidebar:
        st.title("🍫 Sade Agents")
        st.markdown("---")

        # Navigasyon
        st.subheader("Sayfalar")

        pages = {
            "home": ("🏠", "Ana Sayfa"),
            "product_launch": ("🚀", "Urun Lansmanı"),
            "market_analysis": ("📊", "Pazar Analizi"),
            "quality_audit": ("✅", "Kalite Denetimi"),
            "history": ("📜", "Gecmis"),
        }

        # Session state'de sayfa yoksa varsayilan sec
        if "current_page" not in st.session_state:
            st.session_state.current_page = "home"

        # Sayfa butonlari
        for page_id, (icon, label) in pages.items():
            if st.button(
                f"{icon} {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_id else "secondary",
            ):
                st.session_state.current_page = page_id
                st.rerun()

        st.markdown("---")

        # Ayarlar bolumu
        st.subheader("Ayarlar")

        # Tenant ID
        tenant_id = st.text_input(
            "Tenant ID",
            value=st.session_state.get("tenant_id", "default"),
            help="Multi-tenant SaaS icin tenant kimlik",
        )
        st.session_state.tenant_id = tenant_id

        # Feature flags
        st.markdown("##### Ozellikler")

        # Bu ayarlar sadece gorsel, gercek config .env'den gelir
        st.checkbox(
            "Gercek Scraping",
            value=False,
            disabled=True,
            help="FEATURE_REAL_SCRAPING env ile ayarlanir",
        )
        st.checkbox(
            "Firebase Storage",
            value=False,
            disabled=True,
            help="FEATURE_FIREBASE_STORAGE env ile ayarlanir",
        )

        st.markdown("---")

        # Footer
        st.caption("v1.1.0 | Sade Chocolate")

    return st.session_state.current_page
