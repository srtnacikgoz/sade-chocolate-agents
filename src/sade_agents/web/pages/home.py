"""
Sade Agents - Ana Sayfa.

Genel bilgi ve hizli erisim.
"""

import streamlit as st


def render() -> None:
    """Ana sayfa icerigini render eder."""
    st.title("🍫 Sade Agents")
    st.markdown("**Sade Chocolate icin AI destekli is operasyonlari multi-agent sistemi**")

    st.markdown("---")

    # Hizli erisim kartlari
    st.subheader("Hizli Erisim")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container():
            st.markdown("### 🚀 Urun Lansmani")
            st.markdown(
                "Yeni cikolata urunleri icin "
                "lansman stratejisi, marka hikayesi ve pazarlama plani olusturur."
            )
            if st.button("Basla", key="quick_product_launch", use_container_width=True):
                st.session_state.current_page = "product_launch"
                st.rerun()

    with col2:
        with st.container():
            st.markdown("### 📊 Pazar Analizi")
            st.markdown(
                "Rakip fiyatlarini analiz eder, "
                "pazar trendlerini belirler ve fiyatlandirma onerileri sunar."
            )
            if st.button("Basla", key="quick_market_analysis", use_container_width=True):
                st.session_state.current_page = "market_analysis"
                st.rerun()

    with col3:
        with st.container():
            st.markdown("### ✅ Kalite Denetimi")
            st.markdown(
                "Urun kalitesini degerlendirir, "
                "iyilestirme alanlari belirler ve kalite raporu olusturur."
            )
            if st.button("Basla", key="quick_quality_audit", use_container_width=True):
                st.session_state.current_page = "quality_audit"
                st.rerun()

    st.markdown("---")

    # Sistem durumu
    st.subheader("Sistem Durumu")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Yapilandirma")

        try:
            from sade_agents.config import get_settings

            settings = get_settings()

            # API durumu
            if settings.validate_api_key():
                st.success("✅ OpenAI API yapilandirilmis")
            else:
                st.warning("⚠️ OpenAI API anahtari ayarlanmamis")

            # Model
            st.info(f"📦 Model: {settings.openai_model_name}")

            # Feature flags
            st.markdown("**Ozellikler:**")
            scraping_status = "✅ Aktif" if settings.feature_real_scraping else "❌ Pasif"
            firebase_status = "✅ Aktif" if settings.feature_firebase_storage else "❌ Pasif"

            st.text(f"  Gercek Scraping: {scraping_status}")
            st.text(f"  Firebase Storage: {firebase_status}")

        except Exception as e:
            st.error(f"Yapilandirma yuklenemedi: {e}")

    with col2:
        st.markdown("##### Son Islemler")

        try:
            from sade_agents.storage import get_storage

            storage = get_storage()
            tenant_id = st.session_state.get("tenant_id", "default")
            recent = storage.list_by_tenant(tenant_id=tenant_id, limit=5)

            if recent:
                for result in recent:
                    icon = {
                        "product_launch": "🚀",
                        "market_analysis": "📊",
                        "quality_audit": "✅",
                    }.get(result.crew_type, "📋")

                    st.text(
                        f"{icon} {result.crew_type.replace('_', ' ').title()} - "
                        f"{result.created_at.strftime('%d.%m %H:%M')}"
                    )
            else:
                st.info("Henuz islem yapilmamis")

        except Exception as e:
            st.warning(f"Gecmis yuklenemedi: {e}")

    st.markdown("---")

    # Bilgi
    st.caption(
        "Sade Agents, CrewAI tabani uzerine insa edilmis "
        "coklu ajan sistemidir. Her crew farkli is operasyonlarini "
        "otonom olarak yonetir."
    )
