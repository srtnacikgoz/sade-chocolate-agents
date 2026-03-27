"""
Sade Agents - Rakip Yonetimi Sayfasi.

Scraping hedeflerini ekle/duzenle/sil.
"""

import json
from pathlib import Path

import streamlit as st

from sade_agents.config import get_settings


def get_targets_file_path() -> Path:
    """Config dosyasinin yolunu dondurur."""
    settings = get_settings()
    config_path = Path(settings.scraping_targets_file)

    if not config_path.is_absolute():
        # Proje kokunu bul
        project_root = Path(__file__).parent.parent.parent.parent.parent
        config_path = project_root / config_path

    return config_path


def load_targets() -> list[dict]:
    """Mevcut hedefleri yukler."""
    config_path = get_targets_file_path()

    if not config_path.exists():
        return []

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("targets", [])


def save_targets(targets: list[dict]) -> None:
    """Hedefleri kaydeder."""
    config_path = get_targets_file_path()

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"targets": targets}, f, ensure_ascii=False, indent=2)


def render() -> None:
    """Rakip yonetimi sayfasini renderlar."""
    st.title("Rakip Yonetimi")
    st.markdown("Fiyat takibi yapilacak rakip siteleri buradan yonetin.")

    # Mevcut hedefleri yukle
    if "targets" not in st.session_state:
        st.session_state.targets = load_targets()

    # Yeni hedef ekleme formu
    st.subheader("Yeni Rakip Ekle")

    with st.form("add_target"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Kisa Ad",
                placeholder="Orn: migros",
                help="URL'siz, kisa bir tanimlayici",
            )

        with col2:
            description = st.text_input(
                "Aciklama",
                placeholder="Orn: market cikolatalari",
                help="Ne tur urunler aranacak",
            )

        url = st.text_input(
            "Urun Sayfasi URL'i",
            placeholder="Orn: https://www.migros.com.tr/cikolata",
            help="Urunlerin listelendigi sayfa",
        )

        submitted = st.form_submit_button("Ekle", type="primary")

        if submitted:
            if not name or not url:
                st.error("Ad ve URL zorunludur.")
            elif any(t["name"] == name for t in st.session_state.targets):
                st.error(f"'{name}' adinda bir hedef zaten var.")
            elif not url.startswith("http"):
                st.error("URL 'http://' veya 'https://' ile baslamali.")
            else:
                new_target = {
                    "name": name.lower().replace(" ", "_"),
                    "url": url,
                    "description": description or "urunler",
                }
                st.session_state.targets.append(new_target)
                save_targets(st.session_state.targets)
                st.success(f"'{name}' eklendi!")
                st.rerun()

    # Mevcut hedefler
    st.subheader("Mevcut Rakipler")

    if not st.session_state.targets:
        st.info("Henuz rakip eklenmemis. Yukardaki formu kullanarak ekleyin.")
    else:
        for i, target in enumerate(st.session_state.targets):
            with st.expander(f"**{target['name']}** - {target.get('description', '')}"):
                st.markdown(f"**URL:** [{target['url']}]({target['url']})")

                col1, col2 = st.columns([3, 1])

                with col1:
                    new_url = st.text_input(
                        "URL Guncelle",
                        value=target["url"],
                        key=f"url_{i}",
                    )
                    new_desc = st.text_input(
                        "Aciklama Guncelle",
                        value=target.get("description", ""),
                        key=f"desc_{i}",
                    )

                with col2:
                    if st.button("Guncelle", key=f"update_{i}"):
                        st.session_state.targets[i]["url"] = new_url
                        st.session_state.targets[i]["description"] = new_desc
                        save_targets(st.session_state.targets)
                        st.success("Guncellendi!")
                        st.rerun()

                    if st.button("Sil", key=f"delete_{i}", type="secondary"):
                        del st.session_state.targets[i]
                        save_targets(st.session_state.targets)
                        st.success(f"'{target['name']}' silindi!")
                        st.rerun()

    # Bilgi
    st.divider()
    st.caption(
        "Not: Degisiklikler scraping_targets.json dosyasina kaydedilir. "
        "Firebase aktifse oradan da okunur."
    )
