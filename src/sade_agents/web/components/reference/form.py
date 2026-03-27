"""
Reference Form Component for AI Code Generation.

Bu dosya, UI Expert Agent'in dinamik form generation icin kullanacagi
production-ready form component ornegi icerir. Dict-based field configuration
ile esnek ve tip-guvenli form olusturmayi gosterir.

Author: UI Expert Agent
Purpose: Golden example for AI code generation with dynamic forms
"""

from typing import Optional, Callable, Literal, Any
import streamlit as st


def render_form(
    title: str,
    fields: list[dict[str, Any]],
    on_submit: Optional[Callable[[dict], None]] = None,
    submit_label: str = "Gonder"
) -> dict[str, Any] | None:
    """
    Production-ready dynamic form component with validation.

    Dict-based field configuration ile flexible form generation. Her field
    type'a gore dogru Streamlit widget render edilir. Required field validation
    dahil.

    Args:
        title: Form baslik metni (ornek: "Yeni Rakip Ekle")
        fields: Field configuration listesi. Her dict su keyler icerir:
            - name (str): Field identifier (ornek: "product_name")
            - type (str): Field tipi ("text"|"number"|"select"|"textarea")
            - label (str): UI'da gosterilecek etiket
            - required (bool): Zorunlu alan mi?
            - placeholder (str, optional): Input placeholder metni
            - options (list, optional): Selectbox icin secenekler
            - min/max (int, optional): Number input icin limitler
        on_submit: Form submit edildiginde cagirilacak callback function
        submit_label: Submit butonu metni

    Returns:
        dict: Form submit edildiyse ve valid ise field name -> value mapping
        None: Form henuz submit edilmediyse veya validation fail

    Example:
        >>> fields = [
        ...     {
        ...         "name": "competitor_name",
        ...         "type": "text",
        ...         "label": "Rakip Adi",
        ...         "required": True,
        ...         "placeholder": "Orn: Marie Antoinette"
        ...     },
        ...     {
        ...         "name": "url",
        ...         "type": "text",
        ...         "label": "Website URL",
        ...         "required": True,
        ...         "placeholder": "Orn: https://marieantoinette.com.tr"
        ...     },
        ...     {
        ...         "name": "category",
        ...         "type": "select",
        ...         "label": "Kategori",
        ...         "options": ["Kutu Cikolata", "Tablet", "Hediye Seti"],
        ...         "required": False
        ...     }
        ... ]
        >>> data = render_form(
        ...     title="Yeni Rakip Ekle",
        ...     fields=fields,
        ...     submit_label="Rakip Ekle"
        ... )
        >>> if data:
        ...     print(f"Form submitted: {data}")

    Notes:
        - st.form context manager kullanir (built-in submit handling)
        - Required field validation otomaktik
        - Field type'a gore dogru widget render (text_input, number_input, etc.)
        - Session state sadece form icinde (global state kirlenmez)
        - Callback optional (on_submit varsa cagirilir)
    """
    with st.form(key=f"form_{title.replace(' ', '_').lower()}"):
        st.markdown(f"### {title}")

        # Form data storage
        form_data: dict[str, Any] = {}

        # Render each field
        for field in fields:
            name = field["name"]
            field_type = field["type"]
            label = field["label"]
            required = field.get("required", False)
            placeholder = field.get("placeholder", "")

            # Required indicator
            label_display = f"{label} *" if required else label

            # Render appropriate widget based on type
            if field_type == "text":
                value = st.text_input(
                    label=label_display,
                    placeholder=placeholder,
                    key=f"{name}_input"
                )
                form_data[name] = value

            elif field_type == "number":
                min_val = field.get("min", 0)
                max_val = field.get("max", None)
                value = st.number_input(
                    label=label_display,
                    min_value=min_val,
                    max_value=max_val,
                    key=f"{name}_input"
                )
                form_data[name] = value

            elif field_type == "select":
                options = field.get("options", [])
                value = st.selectbox(
                    label=label_display,
                    options=options,
                    key=f"{name}_input"
                )
                form_data[name] = value

            elif field_type == "textarea":
                value = st.text_area(
                    label=label_display,
                    placeholder=placeholder,
                    key=f"{name}_input"
                )
                form_data[name] = value

            else:
                st.error(f"Desteklenmeyen field type: {field_type}")

        # Submit button
        submitted = st.form_submit_button(submit_label)

        if submitted:
            # Validate required fields
            validation_errors = []
            for field in fields:
                if field.get("required", False):
                    name = field["name"]
                    value = form_data.get(name)
                    if not value:
                        label = field["label"]
                        validation_errors.append(f"{label} zorunlu alan")

            # Show validation errors
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                return None

            # Call callback if provided
            if on_submit:
                on_submit(form_data)

            return form_data

    return None


# ============================================================================
# Usage example for AI training
# ============================================================================
"""
ORNEK KULLANIM 1 - Rakip Ekleme Formu:

fields = [
    {
        "name": "name",
        "type": "text",
        "label": "Rakip Adi",
        "required": True,
        "placeholder": "Orn: Vakko Chocolate"
    },
    {
        "name": "url",
        "type": "text",
        "label": "Website URL",
        "required": True,
        "placeholder": "Orn: https://vakkochocolate.com"
    },
    {
        "name": "priority",
        "type": "select",
        "label": "Oncelik",
        "options": ["Yuksek", "Orta", "Dusuk"],
        "required": False
    }
]

data = render_form(
    title="Yeni Rakip Ekle",
    fields=fields,
    submit_label="Rakip Ekle"
)

if data:
    st.success(f"Rakip eklendi: {data['name']}")

ORNEK KULLANIM 2 - Urun Ekleme Formu (Number Input):

fields = [
    {
        "name": "product_name",
        "type": "text",
        "label": "Urun Adi",
        "required": True,
        "placeholder": "Orn: Ruby Truffle Box"
    },
    {
        "name": "price",
        "type": "number",
        "label": "Fiyat (TL)",
        "required": True,
        "min": 0,
        "max": 10000
    },
    {
        "name": "description",
        "type": "textarea",
        "label": "Aciklama",
        "required": False,
        "placeholder": "Urun detaylari..."
    }
]

data = render_form(
    title="Yeni Urun Ekle",
    fields=fields,
    on_submit=lambda d: save_to_firestore(d),
    submit_label="Kaydet"
)

ORNEK KULLANIM 3 - Callback ile Entegrasyon:

def handle_submit(form_data: dict):
    # Firebase'e kaydet
    save_to_firestore("competitors", form_data)
    st.success("Kaydedildi!")
    st.balloons()

data = render_form(
    title="Form Basligi",
    fields=fields,
    on_submit=handle_submit
)

AI GENERATION KURALLARI:
- Field configuration dict-based (flexible, extensible)
- Her field en az: name, type, label, required keyler icerir
- Type hints zorunlu: list[dict[str, Any]], Callable, Optional
- st.form context manager kullan (built-in submit handling)
- Required validation otomatik yap
- Session state global kirlenmemeli (form-scoped keys)
- Callback optional (on_submit: Optional[Callable])
- Supported field types: text, number, select, textarea
- Placeholder her zaman "Orn: ..." formatinda
"""
