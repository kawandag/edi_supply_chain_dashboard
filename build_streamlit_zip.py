"""Package the complete GitHub/Streamlit Cloud deployment."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "supply_chain_streamlit_project.zip"
EXCLUDED_PARTS = {".git", "__pycache__", ".venv", "venv"}
INCLUDED_ROOT_FILES = {
    ".gitignore",
    "app.py",
    "README.md",
    "requirements.txt",
    "build_streamlit_zip.py",
}


def build_archive() -> Path:
    if not (ROOT / "app.py").exists():
        raise FileNotFoundError(f"Streamlit entry point not found at {ROOT / 'app.py'}")

    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
        paths = [ROOT / name for name in INCLUDED_ROOT_FILES]
        paths += list((ROOT / ".github").rglob("*"))
        paths += list((ROOT / ".streamlit").rglob("*"))
        paths += list((ROOT / "supply_chain_streamlit_project").rglob("*"))
        for path in paths:
            if (
                path.is_file()
                and path != OUTPUT
                and not EXCLUDED_PARTS.intersection(path.parts)
            ):
                archive.write(path, path.relative_to(ROOT))
    return OUTPUT


if __name__ == "__main__":
    print(f"Created {build_archive()}")
