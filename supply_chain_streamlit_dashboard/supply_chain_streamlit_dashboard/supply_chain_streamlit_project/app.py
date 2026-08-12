"""Compatibility entry point for the original Streamlit Cloud app path."""

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "supply_chain_streamlit_project" / "app.py"
runpy.run_path(str(APP), run_name="__main__")
