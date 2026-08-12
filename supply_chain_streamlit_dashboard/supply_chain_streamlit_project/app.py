"""Root entry point used by Streamlit Community Cloud."""

from pathlib import Path
import runpy


APP = Path(__file__).parent / "supply_chain_streamlit_project" / "app.py"
runpy.run_path(str(APP), run_name="__main__")
