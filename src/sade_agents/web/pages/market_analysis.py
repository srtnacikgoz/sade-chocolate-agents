"""
Sade Agents - Pazar Analizi Sayfasi.

MarketAnalysisCrew'u calistirmak icin form ve sonuc gorunumu.
"""

import streamlit as st


def render() -> None:
    """Pazar analizi sayfasini render eder."""
    st.title("📊 Pazar Analizi")
    st.markdown("Rakip fiyatlarini analiz edin ve pazarlama stratejisi olusturun.")

    st.markdown("---")

    # Form
    with st.form("market_analysis_form"):
        st.subheader("Analiz Parametreleri")

        col1, col2 = st.columns(2)

        with col1:
            competitor_name = st.selectbox(
                "Rakip *",
                options=[
                    "Vakko",
                    "Godiva",
                    "Lindt",
                    "Butterfly",
                    "Divan",
                    "Marie Antoinette",
                    "Kahve Dunyasi",
                ],
                help="Analiz edilecek rakip",
            )

            product_category = st.selectbox(
                "Urun Kategorisi",
                options=[
                    "premium chocolate",
                    "tablet cikolata",
                    "truffle",
                    "hediye kutusu",
                    "draje",
                ],
                help="Odaklanilacak urun kategorisi",
            )

        with col2:
            include_trends = st.checkbox(
                "Trend Analizi Dahil Et",
                value=True,
                help="GrowthHacker agent ile trend analizi yapilsin mi",
            )

        st.markdown("---")

        submitted = st.form_submit_button(
            "📊 Analizi Baslat",
            use_container_width=True,
            type="primary",
        )

    # Form gonderildiginde
    if submitted:
        # Giris verilerini hazirla (MarketAnalysisInput formatinda)
        inputs = {
            "competitor_name": competitor_name,
            "product_category": product_category,
            "include_trends": include_trends,
        }

        # Crew'u calistir
        _run_crew(inputs)


def _run_crew(inputs: dict) -> None:
    """MarketAnalysisCrew'u calistirir ve sonucu gosterir."""
    st.markdown("---")
    st.subheader("Pazar Analizi Yapiliyor...")

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
        crew = factory.create_crew("market_analysis")

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
        if hasattr(result, "pricing_analysis"):
            outputs["pricing_analysis"] = result.pricing_analysis
        if hasattr(result, "trend_report") and result.trend_report:
            outputs["trend_report"] = result.trend_report
        if hasattr(result, "summary"):
            outputs["summary"] = result.summary
        if hasattr(result, "execution_time_seconds"):
            outputs["execution_time_seconds"] = result.execution_time_seconds

        # Raw output da ekle
        outputs["raw"] = str(result)

        saved_result = storage.create_result(
            crew_type="market_analysis",
            inputs=inputs,
            outputs=outputs,
            tenant_id=tenant_id,
        )

        progress.progress(100)
        status.text("Tamamlandi!")

        # Sonucu goster
        st.success("Pazar analizi basariyla tamamlandi!")

        from sade_agents.web.components.result_viewer import render_result

        render_result(saved_result)

    except Exception as e:
        st.error(f"Bir hata olustu: {e}")
        import traceback

        st.code(traceback.format_exc())
