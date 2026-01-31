"""
Sade Agents - Kalite Denetimi Sayfasi.

QualityAuditCrew'u calistirmak icin form ve sonuc gorunumu.
"""

import streamlit as st


def render() -> None:
    """Kalite denetimi sayfasini render eder."""
    st.title("✅ Kalite Denetimi")
    st.markdown("Icerik kalitesini degerlendirir ve iyilestirme onerileri sunar.")

    st.markdown("---")

    # Form
    with st.form("quality_audit_form"):
        st.subheader("Denetim Bilgileri")

        content = st.text_area(
            "Denetlenecek Icerik *",
            placeholder="Ornek: Sade'nin en yeni lezzeti, Antep'in ustaligi ile bulusuyor.",
            height=150,
            help="Denetlenecek metin veya prompt",
        )

        col1, col2 = st.columns(2)

        with col1:
            content_type = st.selectbox(
                "Icerik Turu *",
                options=[
                    "metin",
                    "gorsel_prompt",
                    "fiyat_analizi",
                    "trend_raporu",
                    "recete",
                ],
                help="Icerik turu - denetim kriterlerini belirler",
            )

        with col2:
            source_agent = st.selectbox(
                "Kaynak Agent *",
                options=[
                    "narrator",
                    "curator",
                    "pricing",
                    "growth",
                    "alchemist",
                ],
                help="Icerigi ureten kaynak agent",
            )

        st.markdown("---")

        submitted = st.form_submit_button(
            "✅ Denetimi Baslat",
            use_container_width=True,
            type="primary",
        )

    # Form gonderildiginde
    if submitted:
        if not content:
            st.error("Denetlenecek icerik zorunludur!")
            return

        # Giris verilerini hazirla (QualityAuditInput formatinda)
        inputs = {
            "content": content,
            "content_type": content_type,
            "source_agent": source_agent,
        }

        # Crew'u calistir
        _run_crew(inputs)


def _run_crew(inputs: dict) -> None:
    """QualityAuditCrew'u calistirir ve sonucu gosterir."""
    st.markdown("---")
    st.subheader("Kalite Denetimi Yapiliyor...")

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
        crew = factory.create_crew("quality_audit")

        # Crew'u calistir
        status.text("AI agentlar calisiyor...")
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
        if hasattr(result, "audit_result"):
            audit = result.audit_result
            outputs["audit_result"] = audit.model_dump() if hasattr(audit, "model_dump") else {
                "overall_score": getattr(audit, "overall_score", 0),
                "verdict": getattr(audit, "verdict", "bilinmiyor"),
                "issues": getattr(audit, "issues", []),
                "suggestions": getattr(audit, "suggestions", []),
                "summary_tr": getattr(audit, "summary_tr", ""),
            }
            outputs["score"] = getattr(audit, "overall_score", 0)
        if hasattr(result, "passed"):
            outputs["passed"] = result.passed
        if hasattr(result, "execution_time_seconds"):
            outputs["execution_time_seconds"] = result.execution_time_seconds

        # Raw output da ekle
        outputs["raw"] = str(result)

        saved_result = storage.create_result(
            crew_type="quality_audit",
            inputs=inputs,
            outputs=outputs,
            tenant_id=tenant_id,
        )

        progress.progress(100)
        status.text("Tamamlandi!")

        # Sonucu goster
        st.success("Kalite denetimi basariyla tamamlandi!")

        from sade_agents.web.components.result_viewer import render_result

        render_result(saved_result)

    except Exception as e:
        st.error(f"Bir hata olustu: {e}")
        import traceback

        st.code(traceback.format_exc())
