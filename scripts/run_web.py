#!/usr/bin/env python3
"""
Sade Agents - Web UI Calistirici.

Streamlit web arayuzunu baslatir.

Kullanim:
    python scripts/run_web.py
    python scripts/run_web.py --port 8502
    python scripts/run_web.py --host 0.0.0.0
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Web UI'yi baslatir."""
    parser = argparse.ArgumentParser(description="Sade Agents Web UI")
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Sunucu portu (varsayilan: 8501)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Sunucu adresi (varsayilan: localhost)",
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        default=True,
        help="Tarayiciyi otomatik ac",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Tarayiciyi otomatik acma",
    )

    args = parser.parse_args()

    # App dosyasinin yolunu bul
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    app_path = project_root / "src" / "sade_agents" / "web" / "app.py"

    if not app_path.exists():
        print(f"Hata: {app_path} bulunamadi!")
        sys.exit(1)

    # Streamlit komutu olustur
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(args.port),
        "--server.address",
        args.host,
    ]

    # Tarayici ayari
    if args.no_browser:
        cmd.extend(["--server.headless", "true"])

    print(f"Sade Agents Web UI baslatiliyor...")
    print(f"Adres: http://{args.host}:{args.port}")
    print("-" * 40)

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nKapatiliyor...")
    except subprocess.CalledProcessError as e:
        print(f"Hata: Streamlit baslatılamadi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
