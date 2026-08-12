"""Package the current Streamlit project without regenerating or overwriting it."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "supply_chain_streamlit_project"
OUTPUT = ROOT / "supply_chain_streamlit_project.zip"


def build_archive() -> Path:
    if not (PROJECT / "app.py").exists():
        raise FileNotFoundError(f"Streamlit app not found at {PROJECT}")

    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
        for path in PROJECT.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(ROOT))
    return OUTPUT


if __name__ == "__main__":
    print(f"Created {build_archive()}")
