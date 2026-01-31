"""
Sade Agents - Urun Lansmani Sayfasi.

ProductLaunchCrew'u calistirmak icin form ve sonuc gorunumu.
"""

import streamlit as st


def render() -> None:
    """Urun lansmani sayfasini render eder."""
    st.title("🚀 Urun Lansmani")
    st.markdown("Yeni cikolata urunleri icin lansman stratejisi olusturun.")

    st.markdown("---")

    # Form
    with st.form("product_launch_form"):
        st.subheader("Urun Bilgileri")

        col1, col2 = st.columns(2)

        with col1:
            flavor_concept = st.text_input(
                "Lezzet Konsepti *",
                placeholder="Antep Fistikli Bitter",
                help="Lansmanini yapacaginiz urunun lezzet konsepti",
            )

            target_audience = st.selectbox(
                "Hedef Kitle",
                options=[
                    "Quiet luxury consumers",
                    "Premium tuketiciler",
                    "Genc profesyoneller",
                    "Hediye alicilar",
                    "Saglik bilincli tuketiciler",
                ],
                help="Urunun birincil hedef kitlesi",
            )

        with col2:
            price_min = st.number_input(
                "Min Fiyat (TL)",
                min_value=50,
                max_value=500,
                value=100,
                step=10,
                help="Minimum fiyat",
            )

            price_max = st.number_input(
                "Max Fiyat (TL)",
                min_value=50,
                max_value=500,
                value=200,
                step=10,
                help="Maksimum fiyat",
            )

        st.markdown("---")

        col3, col4 = st.columns(2)

        with col3:
            include_audit = st.checkbox(
                "Kalite Denetimi Dahil Et",
                value=True,
                help="Perfectionist agent ile denetim yapilsin mi",
            )

        st.markdown("---")

        submitted = st.form_submit_button(
            "🚀 Lansman Planini Olustur",
            use_container_width=True,
            type="primary",
        )

    # Form gonderildiginde
    if submitted:
        if not flavor_concept:
            st.error("Lezzet konsepti zorunludur!")
            return

        if price_max <= price_min:
            st.error("Maksimum fiyat minimum fiyattan buyuk olmali!")
            return

        # Giris verilerini hazirla (ProductLaunchInput formatinda)
        # Scalar degerler kullan - list/tuple YASAK (CrewAI uyumlulugu)
        inputs = {
            "flavor_concept": flavor_concept,
            "target_audience": target_audience,
            "price_range_min": float(price_min),
            "price_range_max": float(price_max),
            "include_audit": include_audit,
        }

        # Crew'u calistir
        _run_crew(inputs)


def _run_crew(inputs: dict) -> None:
    """ProductLaunchCrew'u calistirir ve sonucu gosterir."""
    st.markdown("---")
    st.subheader("Lansman Plani Olusturuluyor...")

    progress = st.progress(0)
    status = st.empty()

    try:
        # Config yukle
        status.text("Yapilandirma yukleniyor...")
        progress.progress(10)

        from sade_agents.config import get_settings

        settings = get_settings()

        if not settings.validate_api_key():
            st.error("OpenAI API anahtari ayarlanmamis! .env dosyasini kontrol edin.")
            return

        # Crew'u yukle
        status.text("Crew hazirlaniyor...")
        progress.progress(20)

        from sade_agents.crews import SadeCrewFactory

        factory = SadeCrewFactory()
        crew = factory.create_crew("product_launch")

        # Crew'u calistir
        status.text("AI agentlar calisiyor (bu birkaç dakika surebilir)...")
        progress.progress(40)

        result = crew.kickoff(inputs=inputs)

        progress.progress(90)

        # Sonucu kaydet
        status.text("Sonuc kaydediliyor...")

        from sade_agents.storage import get_storage

        storage = get_storage()
        tenant_id = st.session_state.get("tenant_id", "default")

        # Output'u dict'e cevir
        outputs = {}
        if hasattr(result, "recipe"):
            outputs["recipe"] = result.recipe
        if hasattr(result, "story"):
            outputs["story"] = result.story
        if hasattr(result, "label_paths"):
            outputs["label_paths"] = result.label_paths
        if hasattr(result, "audit") and result.audit:
            outputs["audit"] = result.audit.model_dump() if hasattr(result.audit, "model_dump") else str(result.audit)
        if hasattr(result, "execution_time_seconds"):
            outputs["execution_time_seconds"] = result.execution_time_seconds

        # Raw output da ekle
        outputs["raw"] = str(result)

        saved_result = storage.create_result(
            crew_type="product_launch",
            inputs=inputs,
            outputs=outputs,
            tenant_id=tenant_id,
        )

        progress.progress(100)
        status.text("Tamamlandi!")

        # Sonucu goster
        st.success("Lansman plani basariyla olusturuldu!")

        from sade_agents.web.components.result_viewer import render_result

        render_result(saved_result)

    except Exception as e:
        st.error(f"Bir hata olustu: {e}")
        import traceback

        st.code(traceback.format_exc())
