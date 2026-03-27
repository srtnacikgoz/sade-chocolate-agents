"""
Sade Agents - UI Generator Sayfasi.

Figma tasarimlarindan Streamlit component kodu ureten AI-destekli arayuz.
UI Expert Agent'in tum becerilerini (design skills, codegen skills, reference library)
bir araya getirir.

AKILLI SISTEM:
- Figma URL'den tasarim verisi cekilir
- Reference library'den pattern ogrenilir
- Type-safe, production-ready kod uretilir
- Verification ile hallucination kontrolu
"""

import streamlit as st
import json
from typing import Optional


def _fetch_design_data(figma_url: str) -> Optional[dict]:
    """
    Figma URL'den tasarim verisini ceker.

    Args:
        figma_url: Figma frame URL'si

    Returns:
        Design data dict veya None (hata durumunda)
    """
    from sade_agents.skills.design_skills import fetch_figma_design

    try:
        result = fetch_figma_design(figma_url)
        return json.loads(result)
    except ValueError as e:
        st.error(f"Gecersiz Figma URL: {e}")
        return None
    except Exception as e:
        st.error(f"Figma verisi cekilemedi: {e}")
        return None


def _generate_code(design_data: dict, component_type: str, function_name: str) -> Optional[str]:
    """
    Design data'dan Streamlit kodu uretir.

    Args:
        design_data: Figma'dan cekilen tasarim verisi
        component_type: Component tipi (card, form, data_table, page)
        function_name: Uretilecek fonksiyon adi

    Returns:
        Generated Python code veya None (hata durumunda)
    """
    from sade_agents.skills.codegen_skills import generate_streamlit_code

    try:
        design_json = json.dumps(design_data)
        code = generate_streamlit_code(design_json, component_type, function_name)
        return code
    except Exception as e:
        st.error(f"Kod uretimi basarisiz: {e}")
        return None


def _verify_code(code: str) -> dict:
    """
    Uretilen kodu dogrular.

    Args:
        code: Dogrulanacak Python kodu

    Returns:
        Verification result dict (valid, issues, suggestions)
    """
    from sade_agents.skills.codegen_skills import verify_generated_code

    try:
        result = verify_generated_code(code)
        return json.loads(result)
    except Exception as e:
        return {
            "valid": False,
            "issues": [f"Verification hatasi: {e}"],
            "suggestions": []
        }


def _load_reference_examples() -> list[dict]:
    """
    Reference component orneklerini yukler.

    Returns:
        Reference ornekleri (name, type, description)
    """
    return [
        {
            "name": "render_card",
            "type": "card",
            "description": "Card component - title, content, icon, variant parametreleri ile esnek kullanim",
            "file": "card.py"
        },
        {
            "name": "render_form",
            "type": "form",
            "description": "Dynamic form - dict-based field config, validation, submit handling",
            "file": "form.py"
        },
        {
            "name": "render_data_table",
            "type": "data_table",
            "description": "Data table - DataFrame rendering, download button, variant options",
            "file": "data_table.py"
        },
    ]


def render_ui_generator_page() -> None:
    """UI Generator sayfasini render eder."""
    st.title("🎨 UI Generator")
    st.markdown("""
    Figma tasarimlarinizdan **production-ready Streamlit kodu** uretin.

    > **Nasil calisir:** Figma URL'sini girin → AI tasarimi analiz eder →
    > Reference library'den pattern ogrenir → Type-safe kod uretir → Hallucination kontrolu yapar
    """)

    st.markdown("---")

    # Form
    with st.form("ui_generator_form"):
        st.subheader("Kod Uretim Parametreleri")

        col1, col2 = st.columns(2)

        with col1:
            figma_url = st.text_input(
                "Figma Frame URL *",
                placeholder="Orn: https://www.figma.com/file/abc123/My-Design?node-id=1:2",
                help="Figma frame'inizin URL'sini yapistiirin (Share > Copy link)"
            )

            component_type = st.selectbox(
                "Component Tipi *",
                options=["card", "form", "data_table", "page"],
                help="Uretilecek component turu"
            )

        with col2:
            function_name = st.text_input(
                "Fonksiyon Adi *",
                placeholder="Orn: render_product_card",
                help="Snake_case format (kucuk harf, alt cizgi ile)",
                value="render_component"
            )

            st.info(
                "💡 **AI-Destekli:** Reference library'den proven patterns kullanilarak\n"
                "hallucination riski minimize edilir."
            )

        st.markdown("---")

        submitted = st.form_submit_button(
            "🚀 Kod Uret",
            use_container_width=True,
            type="primary"
        )

    # Form gonderildiginde
    if submitted:
        if not figma_url:
            st.error("Figma URL gerekli!")
            return

        if not function_name:
            st.error("Fonksiyon adi gerekli!")
            return

        # Fonksiyon adi validation
        if not function_name.replace("_", "").isalnum():
            st.error("Fonksiyon adi sadece harf, rakam ve alt cizgi icermelidir!")
            return

        # Generation flow
        _run_generation(figma_url, component_type, function_name)

    # Reference Library bolumu
    st.markdown("---")
    with st.expander("📚 Reference Component Ornekleri"):
        st.markdown("""
        **Reference Library:** AI'nin kod uretirken kullandigi proven patterns.

        Bu ornekler:
        - ✅ Type hints (full type safety)
        - ✅ Google-style docstrings
        - ✅ Usage examples
        - ✅ Sade styling conventions
        - ✅ No hardcoded values
        """)

        examples = _load_reference_examples()

        for example in examples:
            st.markdown(f"**{example['name']}** (`{example['type']}`)")
            st.caption(example['description'])
            st.markdown("")


def _run_generation(figma_url: str, component_type: str, function_name: str) -> None:
    """
    UI generation flow'unu calistirir.

    Args:
        figma_url: Figma frame URL'si
        component_type: Component tipi
        function_name: Fonksiyon adi
    """
    st.markdown("---")
    st.subheader("🔄 Kod Uretiliyor...")

    progress = st.progress(0)
    status = st.empty()

    # Step 1: Fetch design data
    status.text("Figma tasarimi cekiliyor...")
    progress.progress(20)

    design_data = _fetch_design_data(figma_url)
    if not design_data:
        progress.progress(100)
        return

    # Step 2: Generate code
    status.text("Streamlit kodu uretiliyor...")
    progress.progress(50)

    code = _generate_code(design_data, component_type, function_name)
    if not code:
        progress.progress(100)
        return

    # Step 3: Verify code
    status.text("Kod dogrulanıyor (hallucination check)...")
    progress.progress(80)

    verification = _verify_code(code)

    progress.progress(100)
    status.text("Tamamlandi!")

    # Display results
    st.success("Kod basariyla uretildi!")

    # Tabs for different views
    tab_code, tab_verify, tab_design = st.tabs(["📝 Generated Code", "✅ Verification", "🎨 Design Data"])

    with tab_code:
        st.markdown("### Generated Streamlit Code")
        st.code(code, language="python")

        # Download button
        st.download_button(
            label="📥 Kodu Indir (.py)",
            data=code,
            file_name=f"{function_name}.py",
            mime="text/plain"
        )

    with tab_verify:
        st.markdown("### Verification Results")

        if verification.get("valid", False):
            st.success("✅ Kod verification'dan gecti!")
        else:
            st.warning("⚠️ Bazi sorunlar bulundu:")

            issues = verification.get("issues", [])
            for issue in issues:
                st.error(f"- {issue}")

        suggestions = verification.get("suggestions", [])
        if suggestions:
            st.markdown("**Oneriler:**")
            for suggestion in suggestions:
                st.info(f"💡 {suggestion}")

    with tab_design:
        st.markdown("### Figma Design Data")
        st.json(design_data)


def render() -> None:
    """Sayfa render fonksiyonu (app.py compatibility icin)."""
    render_ui_generator_page()


__all__ = ["render_ui_generator_page", "render"]
