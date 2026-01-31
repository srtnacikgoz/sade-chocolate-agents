"""
Sade Agents - Gecmis Sayfasi.

Onceki crew sonuclarini listeler ve detaylarini gosterir.
"""

import streamlit as st


def render() -> None:
    """Gecmis sayfasini render eder."""
    st.title("📜 Gecmis")
    st.markdown("Onceki crew sonuclarini inceleyin.")

    st.markdown("---")

    # Filtreler
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        crew_filter = st.selectbox(
            "Crew Turu",
            options=["Tumu", "product_launch", "market_analysis", "quality_audit"],
            format_func=lambda x: {
                "Tumu": "🗂️ Tum Crew'lar",
                "product_launch": "🚀 Urun Lansmani",
                "market_analysis": "📊 Pazar Analizi",
                "quality_audit": "✅ Kalite Denetimi",
            }.get(x, x),
        )

    with col2:
        limit = st.selectbox(
            "Gosterilecek Sayi",
            options=[10, 25, 50, 100],
            index=0,
        )

    with col3:
        show_deleted = st.checkbox("Silinmisleri goster", value=False)

    st.markdown("---")

    # Sonuclari yukle
    try:
        from sade_agents.storage import get_storage

        storage = get_storage()
        tenant_id = st.session_state.get("tenant_id", "default")

        crew_type = None if crew_filter == "Tumu" else crew_filter

        results = storage.list_by_tenant(
            tenant_id=tenant_id,
            crew_type=crew_type,
            include_deleted=show_deleted,
            limit=limit,
        )

        if not results:
            st.info("Henuz sonuc bulunmuyor.")
            return

        st.subheader(f"Toplam {len(results)} sonuc")

        # Sonuclari listele
        for result in results:
            _render_result_row(result, storage)

    except Exception as e:
        st.error(f"Sonuclar yuklenirken hata: {e}")
        import traceback

        st.code(traceback.format_exc())


def _render_result_row(result, storage) -> None:
    """Tek bir sonucu satir olarak gosterir."""
    from sade_agents.storage.base import CrewResult

    crew_icons = {
        "product_launch": "🚀",
        "market_analysis": "📊",
        "quality_audit": "✅",
    }

    icon = crew_icons.get(result.crew_type, "📋")
    is_deleted = result.is_deleted

    # Container
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])

        with col1:
            if is_deleted:
                st.markdown(f"~~{icon}~~")
            else:
                st.markdown(f"## {icon}")

        with col2:
            title = result.crew_type.replace("_", " ").title()
            if is_deleted:
                st.markdown(f"~~**{title}**~~")
                st.caption("Silindi")
            else:
                st.markdown(f"**{title}**")

            st.caption(
                f"ID: {result.result_id[:8]}... | "
                f"Tarih: {result.created_at.strftime('%d.%m.%Y %H:%M')}"
            )

            # Giris ozeti
            if result.inputs:
                input_preview = _get_input_preview(result.inputs, result.crew_type)
                st.text(input_preview)

        with col3:
            # Sonuc ozeti
            if result.outputs and "raw" in result.outputs:
                output_preview = result.outputs["raw"][:100] + "..."
                st.text(output_preview)

        with col4:
            # Aksiyonlar
            col_detail, col_delete = st.columns(2)

            with col_detail:
                if st.button("📄 Detay", key=f"detail_{result.result_id}"):
                    st.session_state.selected_result_id = result.result_id
                    st.session_state.show_detail_modal = True
                    st.rerun()

            with col_delete:
                if not is_deleted:
                    if st.button("🗑️ Sil", key=f"delete_{result.result_id}"):
                        storage.soft_delete(result.result_id, result.tenant_id)
                        st.success("Silindi!")
                        st.rerun()

        st.markdown("---")

    # Detay modal
    if (
        st.session_state.get("show_detail_modal")
        and st.session_state.get("selected_result_id") == result.result_id
    ):
        _show_detail_modal(result)


def _get_input_preview(inputs: dict, crew_type: str) -> str:
    """Giris parametrelerinin kisa ozetini olusturur."""
    if crew_type == "product_launch":
        urun = inputs.get("urun_adi", "Bilinmiyor")
        hedef = inputs.get("hedef_kitle", "")
        return f"Urun: {urun} | Hedef: {hedef}"

    if crew_type == "market_analysis":
        tur = inputs.get("analiz_turu", "Bilinmiyor")
        segment = ", ".join(inputs.get("hedef_segment", []))
        return f"Tur: {tur} | Segment: {segment}"

    if crew_type == "quality_audit":
        urun = inputs.get("urun_adi", "Bilinmiyor")
        tur = inputs.get("denetim_turu", "")
        return f"Urun: {urun} | Tur: {tur}"

    return str(inputs)[:80] + "..."


def _show_detail_modal(result) -> None:
    """Detay modalini gosterir."""
    with st.expander("📋 Sonuc Detayi", expanded=True):
        from sade_agents.web.components.result_viewer import render_result

        render_result(result)

        if st.button("Kapat", key="close_modal"):
            st.session_state.show_detail_modal = False
            st.session_state.selected_result_id = None
            st.rerun()
