"""
Sade Agents - Web UI modulu.

Streamlit tabanli web arayuzu.
"""

__all__ = ["run_app"]


def run_app() -> None:
    """Streamlit uygulamasini baslatir."""
    import subprocess
    import sys
    from pathlib import Path

    app_path = Path(__file__).parent / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=True)
