"""
Sade Agents - Code Generation Skills.

Figma tasarimindan Streamlit kodu uretme ve dogrulama.
Reference component library'den pattern ogrenip production-ready kod uretir.
"""

from crewai.tools import tool
from typing import Dict, Any, List
from pathlib import Path
import ast
import json
import logging
import re

logger = logging.getLogger(__name__)

# Gecerli Streamlit API'leri (hallucination kontrolu icin)
VALID_STREAMLIT_APIS = {
    # Layout
    "st.container", "st.columns", "st.expander", "st.tabs", "st.sidebar",
    # Text
    "st.write", "st.markdown", "st.title", "st.header", "st.subheader",
    "st.caption", "st.text", "st.code", "st.latex",
    # Data
    "st.dataframe", "st.table", "st.metric", "st.json",
    # Input
    "st.button", "st.download_button", "st.checkbox", "st.radio",
    "st.selectbox", "st.multiselect", "st.slider", "st.text_input",
    "st.text_area", "st.number_input", "st.date_input", "st.time_input",
    "st.file_uploader", "st.color_picker",
    # Media
    "st.image", "st.audio", "st.video",
    # Status
    "st.success", "st.info", "st.warning", "st.error", "st.spinner",
    "st.progress", "st.balloons", "st.snow",
    # Form
    "st.form", "st.form_submit_button",
    # State
    "st.session_state", "st.rerun",
    # Other
    "st.empty", "st.divider", "st.toast",
}


@tool
def load_reference_examples(component_type: str = "all") -> str:
    """
    Reference component library'den ornek kodlari yukler.

    AI kod uretirken bu ornekleri pattern olarak kullanir.
    Hallucination'i minimize etmek icin sadece gercek kod ornekleri saglar.

    Args:
        component_type: "card" | "form" | "data_table" | "all"

    Returns:
        Reference kod ornekleri (Python string)

    Example:
        >>> examples = load_reference_examples("card")
        >>> print(examples)  # card.py icerigi
    """
    reference_dir = Path("src/sade_agents/web/components/reference")

    if not reference_dir.exists():
        logger.warning(f"Reference directory not found: {reference_dir}")
        return "# Reference library not found. Use standard Streamlit patterns."

    examples = []

    if component_type == "all":
        files = ["card.py", "form.py", "data_table.py"]
    else:
        files = [f"{component_type}.py"]

    for filename in files:
        filepath = reference_dir / filename
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            examples.append(f"# === {filename} ===\n{content}\n")
        else:
            logger.warning(f"Reference file not found: {filepath}")

    if not examples:
        return "# No reference examples found."

    return "\n".join(examples)


@tool
def generate_streamlit_code(
    design_json: str,
    component_type: str,
    component_name: str
) -> str:
    """
    Design data'dan Streamlit component kodu uretir.

    Reference library'deki pattern'lari takip ederek
    type hints, docstring ve Sade styling ile kod uretir.

    Args:
        design_json: fetch_figma_design'dan donen JSON
        component_type: "card" | "form" | "data_table" | "page"
        component_name: Fonksiyon adi (snake_case, Orn: "render_product_card")

    Returns:
        Python kodu (string)

    Note:
        Bu fonksiyon sablondan kod uretir.
        Gercek AI generation icin LLM entegrasyonu gerekir.

    Example:
        >>> code = generate_streamlit_code(design_json, "card", "render_product_card")
        >>> print(code)  # Streamlit component kodu
    """
    try:
        design = json.loads(design_json)
    except json.JSONDecodeError:
        design = {}

    # Design tokens
    colors = design.get("colors", ["#FAFAF8", "#2C2C2C", "#8B7355"])
    spacing = design.get("spacing", {"padding": 40, "gap": 16})
    frame_name = design.get("frame_name", "Component")

    # Component type'a gore template sec
    if component_type == "card":
        code = _generate_card_template(component_name, frame_name, colors)
    elif component_type == "form":
        code = _generate_form_template(component_name, frame_name)
    elif component_type == "data_table":
        code = _generate_table_template(component_name, frame_name)
    else:
        code = _generate_page_template(component_name, frame_name, design)

    logger.info(f"Kod uretildi: {component_name} ({component_type})")
    return code


@tool
def verify_generated_code(code: str) -> str:
    """
    Uretilen Streamlit kodunu dogrular.

    Kontroller:
    1. Syntax gecerliligi (ast.parse)
    2. Type hints varmi
    3. Docstring varmi
    4. Streamlit API'leri gecerli mi (hallucination kontrolu)
    5. Hardcoded degerler var mi

    Args:
        code: Dogrulanacak Python kodu

    Returns:
        JSON string:
        - valid: bool
        - issues: list[str]
        - suggestions: list[str]

    Example:
        >>> result = verify_generated_code("def foo(): st.card()")
        >>> data = json.loads(result)
        >>> print(data["valid"])  # False (st.card yok)
    """
    issues: List[str] = []
    suggestions: List[str] = []

    # 1. Syntax check
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return json.dumps({
            "valid": False,
            "issues": [f"Syntax hatasi: {e}"],
            "suggestions": ["Kodu duzeltin ve tekrar deneyin"],
        })

    # 2. Type hints check
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    for func in functions:
        if not func.returns:
            issues.append(f"Fonksiyon '{func.name}' return type hint eksik")

        # Args type hints
        for arg in func.args.args:
            if arg.annotation is None and arg.arg != "self":
                issues.append(f"Fonksiyon '{func.name}', parametre '{arg.arg}' type hint eksik")

    # 3. Docstring check
    for func in functions:
        docstring = ast.get_docstring(func)
        if not docstring:
            issues.append(f"Fonksiyon '{func.name}' docstring eksik")

    # 4. Streamlit API check (hallucination kontrolu)
    st_calls = re.findall(r'st\.\w+', code)
    for call in st_calls:
        if call not in VALID_STREAMLIT_APIS:
            issues.append(f"Gecersiz Streamlit API: {call} (hallucination?)")

    # 5. Hardcoded values check
    hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', code)
    if len(hex_colors) > 2:
        suggestions.append(f"Cok fazla hardcoded renk ({len(hex_colors)}). Variables kullanin.")

    magic_numbers = re.findall(r'\b\d{3,}\b', code)
    if magic_numbers:
        suggestions.append(f"Magic numbers bulundu: {magic_numbers[:3]}. Constants kullanin.")

    # Result
    valid = len(issues) == 0
    if valid:
        suggestions.append("Kod verification'dan gecti!")

    return json.dumps({
        "valid": valid,
        "issues": issues,
        "suggestions": suggestions,
    }, ensure_ascii=False, indent=2)


# === Template Functions (Internal) ===

def _generate_card_template(name: str, title: str, colors: list) -> str:
    """Card component template."""
    return f'''"""
Sade Chocolate - {title} Card Component.

Figma tasarimindan otomatik uretildi.
"""
import streamlit as st
from typing import Optional


def {name}(
    title: str,
    content: str,
    icon: Optional[str] = None,
) -> None:
    """
    {title} kartini render eder.

    Args:
        title: Kart basligi
        content: Kart icerigi
        icon: Opsiyonel emoji/icon
    """
    with st.container():
        col1, col2 = st.columns([1, 20])

        if icon:
            col1.markdown(f"### {{icon}}")

        col2.markdown(f"### {{title}}")
        col2.markdown(content)


# Usage example:
# {name}("Baslik", "Icerik metni", icon="📦")
'''


def _generate_form_template(name: str, title: str) -> str:
    """Form component template."""
    return f'''"""
Sade Chocolate - {title} Form Component.

Figma tasarimindan otomatik uretildi.
"""
import streamlit as st
from typing import Dict, Any, Optional


def {name}(
    on_submit: Optional[callable] = None,
) -> Dict[str, Any] | None:
    """
    {title} formunu render eder.

    Args:
        on_submit: Form submit callback

    Returns:
        Form verileri veya None
    """
    with st.form(key="{name}_form"):
        st.subheader("{title}")

        # Form alanlari
        field1 = st.text_input("Alan 1", placeholder="Orn: Deger")
        field2 = st.text_area("Aciklama", placeholder="Detaylar...")

        submitted = st.form_submit_button("Gonder")

        if submitted:
            data = {{"field1": field1, "field2": field2}}
            if on_submit:
                on_submit(data)
            return data

    return None


# Usage example:
# result = {name}(on_submit=lambda d: print(d))
'''


def _generate_table_template(name: str, title: str) -> str:
    """Data table component template."""
    return f'''"""
Sade Chocolate - {title} Table Component.

Figma tasarimindan otomatik uretildi.
"""
import streamlit as st
import pandas as pd
from typing import Literal


def {name}(
    data: pd.DataFrame,
    show_download: bool = True,
) -> None:
    """
    {title} tablosunu render eder.

    Args:
        data: Gosterilecek DataFrame
        show_download: CSV indirme butonu goster
    """
    st.subheader("{title}")
    st.dataframe(data, use_container_width=True)

    if show_download:
        csv = data.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="CSV Indir",
            data=csv,
            file_name="{name}.csv",
            mime="text/csv",
        )


# Usage example:
# df = pd.DataFrame({{"A": [1, 2], "B": [3, 4]}})
# {name}(df)
'''


def _generate_page_template(name: str, title: str, design: dict) -> str:
    """Full page template."""
    components = design.get("components", [])
    component_code = ""

    for comp in components:
        comp_type = comp.get("type", "text")
        if comp_type == "text":
            component_code += f'    st.markdown("{comp.get("content", "")}")\n'
        elif comp_type == "button":
            component_code += f'    st.button("{comp.get("content", "Button")}")\n'
        elif comp_type == "container":
            component_code += f'    with st.container():\n        st.write("Container content")\n'

    if not component_code:
        component_code = '    st.write("Page content")\n'

    return f'''"""
Sade Chocolate - {title} Page.

Figma tasarimindan otomatik uretildi.
"""
import streamlit as st


def {name}() -> None:
    """
    {title} sayfasini render eder.
    """
    st.title("{title}")

{component_code}

# Usage:
# {name}()
'''


__all__ = [
    "load_reference_examples",
    "generate_streamlit_code",
    "verify_generated_code",
    "VALID_STREAMLIT_APIS",
]
