"""
Reference Data Table Component for AI Code Generation.

Bu dosya, UI Expert Agent'in tabular data rendering icin kullanacagi
production-ready data table component ornegi icerir. Pandas DataFrame ile
entegre, download destegiyle.

Author: UI Expert Agent
Purpose: Golden example for AI code generation with data tables
"""

from typing import Literal
import streamlit as st
import pandas as pd


def render_data_table(
    data: pd.DataFrame,
    title: str,
    variant: Literal["default", "compact", "striped"] = "default",
    show_download: bool = True
) -> None:
    """
    Production-ready data table component with download support.

    Pandas DataFrame'i Streamlit ile render eder. Variant'a gore farkli
    display modlari (default table, compact dataframe, striped dataframe).
    CSV download butonu optional.

    Args:
        data: Gosterilecek pandas DataFrame
        title: Tablo baslik metni (ornek: "Rakip Urunleri")
        variant: Display modu
            - "default": st.table (static, clean)
            - "compact": st.dataframe (interactive, scrollable)
            - "striped": st.dataframe with alternating row colors
        show_download: CSV download butonu goster?

    Returns:
        None (UI render eder)

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "Urun": ["Ruby Truffle", "Dark Ganache", "Milk Praline"],
        ...     "Fiyat": [450, 380, 320],
        ...     "Rakip": ["Marie Antoinette", "Vakko", "Godiva"]
        ... })
        >>> render_data_table(
        ...     data=df,
        ...     title="Rakip Urun Analizi",
        ...     variant="compact",
        ...     show_download=True
        ... )

    Notes:
        - st.table: Static, best for small datasets (<50 rows)
        - st.dataframe: Interactive, sortable, scrollable (large datasets)
        - CSV download: to_csv() ile UTF-8 encoding
        - Title: st.markdown ile header render
        - Empty DataFrame kontrolu (graceful fallback)
    """
    # Header
    st.markdown(f"### {title}")

    # Empty check
    if data.empty:
        st.info("Gosterilecek veri yok")
        return

    # Render table based on variant
    if variant == "default":
        # Static table (clean, no interaction)
        st.table(data)

    elif variant == "compact":
        # Interactive dataframe (compact mode)
        st.dataframe(data, use_container_width=True)

    elif variant == "striped":
        # Interactive dataframe with styling
        st.dataframe(
            data,
            use_container_width=True,
            height=min(len(data) * 35 + 38, 400)  # Auto-height with max
        )

    else:
        st.error(f"Desteklenmeyen variant: {variant}")
        return

    # Download button
    if show_download:
        csv_data = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 CSV Indir",
            data=csv_data,
            file_name=f"{title.replace(' ', '_').lower()}.csv",
            mime="text/csv"
        )


# ============================================================================
# Usage example for AI training
# ============================================================================
"""
ORNEK KULLANIM 1 - Basit Tablo (Default):

import pandas as pd

df = pd.DataFrame({
    "Rakip": ["Marie Antoinette", "Vakko Chocolate", "Godiva"],
    "Urun Sayisi": [45, 32, 67],
    "Ortalama Fiyat": [425, 380, 520]
})

render_data_table(
    data=df,
    title="Rakip Ozeti",
    variant="default"
)

ORNEK KULLANIM 2 - Buyuk Dataset (Compact):

# 100+ satir icin compact mod daha uygun
df = pd.read_csv("competitor_products.csv")

render_data_table(
    data=df,
    title="Tum Rakip Urunleri",
    variant="compact",
    show_download=True  # CSV download etkinlestirildi
)

ORNEK KULLANIM 3 - Striped (Okunabilirlik):

df = pd.DataFrame({
    "Tarih": ["2024-01-15", "2024-01-16", "2024-01-17"],
    "Yeni Urun": ["Ruby Box", "Dark Collection", "Milk Truffle"],
    "Rakip": ["Marie", "Vakko", "Godiva"],
    "Fiyat": [450, 380, 420]
})

render_data_table(
    data=df,
    title="Son 7 Gunde Tespit Edilen Urunler",
    variant="striped"
)

ORNEK KULLANIM 4 - Bos DataFrame Durumu:

df = pd.DataFrame(columns=["Urun", "Fiyat", "Rakip"])  # Bos

render_data_table(
    data=df,
    title="Bugun Tespit Edilen Urunler",
    variant="compact"
)
# Output: "Gosterilecek veri yok" info mesaji

ORNEK KULLANIM 5 - Download Devre Disi:

render_data_table(
    data=df,
    title="Internal Data (No Download)",
    variant="compact",
    show_download=False  # Download butonu gizlendi
)

AI GENERATION KURALLARI:
- Her zaman pd.DataFrame type hint kullan
- Empty DataFrame kontrolu yap (data.empty)
- Variant: "default" (<=50 row), "compact" (>50 row, scrollable)
- CSV download: to_csv(index=False).encode('utf-8')
- File name: title'dan turet (lowercase, underscores)
- use_container_width=True (responsive)
- Height: otomatik hesapla (rows * 35 + 38 header, max 400px)
- Title: st.markdown ile ### header
"""
