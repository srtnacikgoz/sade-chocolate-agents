"""
Sade Agents - Result Viewer Component.

Crew sonuclarini gostermek icin bilesken.
"""

import streamlit as st

from sade_agents.storage.base import CrewResult


def render_result(result: CrewResult) -> None:
    """
    Crew sonucunu gorsel olarak gosterir.

    Args:
        result: Gosterilecek CrewResult
    """
    # Baslik ve meta bilgi
    crew_labels = {
        "product_launch": "🚀 Urun Lansmani",
        "market_analysis": "📊 Pazar Analizi",
        "quality_audit": "✅ Kalite Denetimi",
    }

    crew_label = crew_labels.get(result.crew_type, result.crew_type)

    st.subheader(f"{crew_label} Sonucu")

    # Meta bilgiler
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ID", result.result_id[:8] + "...")
    with col2:
        st.metric("Tarih", result.created_at.strftime("%d.%m.%Y %H:%M"))
    with col3:
        st.metric("Tenant", result.tenant_id)

    st.markdown("---")

    # Giris parametreleri
    with st.expander("📥 Giris Parametreleri", expanded=False):
        st.json(result.inputs)

    # Cikis sonuclari
    st.subheader("📤 Sonuclar")

    outputs = result.outputs

    # Farkli crew tiplerine gore gosterim
    if result.crew_type == "product_launch":
        _render_product_launch_result(outputs)
    elif result.crew_type == "market_analysis":
        _render_market_analysis_result(outputs)
    elif result.crew_type == "quality_audit":
        _render_quality_audit_result(outputs)
    else:
        # Genel gosterim
        st.json(outputs)


def _parse_json_from_raw(raw_output: str) -> dict | None:
    """Raw output'tan JSON parse eder."""
    import json
    import re

    if not raw_output:
        return None

    # JSON bloğunu bul (```json ... ``` veya { ... })
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', raw_output)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Direkt JSON dene
    try:
        # İlk { ve son } arasını al
        start = raw_output.find('{')
        end = raw_output.rfind('}')
        if start != -1 and end != -1:
            return json.loads(raw_output[start:end+1])
    except json.JSONDecodeError:
        pass

    return None


def _render_product_launch_result(outputs: dict) -> None:
    """Urun lansmani sonucunu gosterir - gelismis UI."""

    # Execution time göster
    if "execution_time_seconds" in outputs:
        elapsed = outputs["execution_time_seconds"]
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        st.info(f"⏱️ Toplam süre: {minutes} dakika {seconds} saniye")

    # Recipe bölümü
    if "recipe" in outputs:
        with st.expander("🍫 **Reçete** (Alchemist)", expanded=True):
            recipe_data = _parse_json_from_raw(outputs["recipe"].get("raw_output", ""))
            if recipe_data:
                _render_audit_card(recipe_data)
            else:
                st.markdown(outputs["recipe"].get("raw_output", "Veri yok"))

    # Story bölümü
    if "story" in outputs:
        with st.expander("✍️ **Hikaye & İçerik** (Narrator)", expanded=True):
            story_data = _parse_json_from_raw(outputs["story"].get("raw_output", ""))
            if story_data:
                _render_audit_card(story_data)
            else:
                st.markdown(outputs["story"].get("raw_output", "Veri yok"))

    # Label paths
    if "label_paths" in outputs and outputs["label_paths"]:
        with st.expander("🎨 **Etiket Görselleri** (Curator)", expanded=True):
            for path in outputs["label_paths"]:
                st.image(path)

    # Audit bölümü
    if "audit" in outputs and outputs["audit"]:
        with st.expander("✅ **Kalite Denetimi** (Perfectionist)", expanded=True):
            if isinstance(outputs["audit"], dict):
                _render_audit_card(outputs["audit"])
            else:
                st.write(outputs["audit"])

    # Raw output (debug için)
    if "raw" in outputs:
        with st.expander("🔍 Ham Çıktı (Debug)", expanded=False):
            st.code(outputs["raw"], language="text")


def _render_audit_card(data: dict) -> None:
    """Audit/skor kartını güzel gösterir."""

    # Skor gösterimi
    if "overall_score" in data:
        score = data["overall_score"]

        # Renk ve emoji belirle
        if score >= 80:
            color, emoji, status = "green", "✅", "Mükemmel"
        elif score >= 60:
            color, emoji, status = "orange", "⚠️", "İyi"
        else:
            color, emoji, status = "red", "❌", "Düşük"

        # Skor kartları
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Genel Skor", f"{score}/100", delta=status)
        with col2:
            if "tone_score" in data:
                st.metric("Ton Uyumu", f"{data['tone_score']}/100")
        with col3:
            if "vocabulary_score" in data:
                st.metric("Kelime", f"{data['vocabulary_score']}/100")
        with col4:
            if "structure_score" in data:
                st.metric("Yapı", f"{data['structure_score']}/100")

        st.markdown("---")

    # Verdict (Karar)
    if "verdict" in data:
        verdict = data["verdict"]
        verdict_display = {
            "onay": ("✅ ONAYLANDI", "success"),
            "revizyon": ("⚠️ REVİZYON GEREKLİ", "warning"),
            "red": ("❌ REDDEDİLDİ", "error"),
        }
        text, msg_type = verdict_display.get(verdict, (verdict, "info"))

        if msg_type == "success":
            st.success(text)
        elif msg_type == "warning":
            st.warning(text)
        elif msg_type == "error":
            st.error(text)
        else:
            st.info(text)

    # Özet
    if "summary_tr" in data:
        st.markdown(f"**Özet:** {data['summary_tr']}")

    # Sorunlar
    if "issues" in data and data["issues"]:
        st.markdown("**🔴 Tespit Edilen Sorunlar:**")
        for issue in data["issues"]:
            st.markdown(f"- {issue}")

    # Öneriler
    if "suggestions" in data and data["suggestions"]:
        st.markdown("**💡 Öneriler:**")
        for suggestion in data["suggestions"]:
            st.markdown(f"- {suggestion}")


def _render_market_analysis_result(outputs: dict) -> None:
    """Pazar analizi sonucunu gosterir - gelismis UI."""

    # Execution time
    if "execution_time_seconds" in outputs:
        elapsed = outputs["execution_time_seconds"]
        st.info(f"⏱️ Analiz süresi: {int(elapsed)} saniye")

    # Fiyat Analizi
    if "pricing_analysis" in outputs:
        with st.expander("💰 **Fiyat Analizi** (Pricing Analyst)", expanded=True):
            pricing = outputs["pricing_analysis"]
            if isinstance(pricing, dict) and "raw_output" in pricing:
                st.markdown(pricing["raw_output"])
            else:
                st.write(pricing)

    # Trend Raporu
    if "trend_report" in outputs and outputs["trend_report"]:
        with st.expander("📈 **Trend Raporu** (Growth Hacker)", expanded=True):
            trend = outputs["trend_report"]
            if isinstance(trend, dict) and "raw_output" in trend:
                st.markdown(trend["raw_output"])
            else:
                st.write(trend)

    # Özet
    if "summary" in outputs:
        st.markdown("---")
        st.markdown("### 📝 Özet")
        st.markdown(f"> {outputs['summary']}")

    # Raw output (debug)
    if "raw" in outputs:
        with st.expander("🔍 Ham Çıktı (Debug)", expanded=False):
            st.code(outputs["raw"], language="text")


def _render_quality_audit_result(outputs: dict) -> None:
    """Kalite denetimi sonucunu gosterir - gelismis UI."""

    # Execution time
    if "execution_time_seconds" in outputs:
        elapsed = outputs["execution_time_seconds"]
        st.info(f"⏱️ Denetim süresi: {int(elapsed)} saniye")

    # Geçti mi?
    if "passed" in outputs:
        if outputs["passed"]:
            st.success("✅ **KALİTE DENETİMİ BAŞARILI**")
        else:
            st.warning("⚠️ **DENETİM: İYİLEŞTİRME GEREKLİ**")

    # Audit Result
    if "audit_result" in outputs:
        audit = outputs["audit_result"]
        if isinstance(audit, dict):
            _render_audit_card(audit)
        else:
            st.write(audit)

    # Raw output (debug)
    if "raw" in outputs:
        with st.expander("🔍 Ham Çıktı (Debug)", expanded=False):
            st.code(outputs["raw"], language="text")


def render_result_card(result: CrewResult) -> bool:
    """
    Sonucu kart olarak gosterir (liste gorunumu icin).

    Args:
        result: Gosterilecek CrewResult

    Returns:
        Detay butonuna tiklanip tiklanmadigi
    """
    crew_icons = {
        "product_launch": "🚀",
        "market_analysis": "📊",
        "quality_audit": "✅",
    }

    icon = crew_icons.get(result.crew_type, "📋")

    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            st.markdown(f"## {icon}")

        with col2:
            st.markdown(f"**{result.crew_type.replace('_', ' ').title()}**")
            st.caption(f"{result.created_at.strftime('%d.%m.%Y %H:%M')} | ID: {result.result_id[:8]}...")

            # Kisa ozet
            if "raw" in result.outputs:
                preview = result.outputs["raw"][:150] + "..."
                st.text(preview)

        with col3:
            clicked = st.button("Detay", key=f"detail_{result.result_id}")

        st.markdown("---")

        return clicked
