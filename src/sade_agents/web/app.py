"""
Sade Agents - Ana Streamlit Uygulamasi.

Crew'lari calistirmak icin web arayuzu.
"""

import streamlit as st

# Sayfa yapilandirmasi
st.set_page_config(
    page_title="Sade Agents",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Ana uygulama."""
    # Sidebar ile navigasyon
    from sade_agents.web.components.sidebar import render_sidebar

    page = render_sidebar()

    # Sayfa icerigini goster
    if page == "home":
        from sade_agents.web.pages.home import render

        render()
    elif page == "product_launch":
        from sade_agents.web.pages.product_launch import render

        render()
    elif page == "market_analysis":
        from sade_agents.web.pages.market_analysis import render

        render()
    elif page == "quality_audit":
        from sade_agents.web.pages.quality_audit import render

        render()
    elif page == "competitors":
        from sade_agents.web.pages.competitors import render

        render()
    elif page == "ui_generator":
        from sade_agents.web.pages.ui_generator import render

        render()
    elif page == "history":
        from sade_agents.web.pages.history import render

        render()


if __name__ == "__main__":
    main()
