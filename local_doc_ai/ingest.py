# ingest.py

from pathlib import Path
import chardet
from unstructured.partition.auto import partition
from unstructured.documents.elements import NarrativeText
from .database import Document, get_session

# Setze den Pfad zum Sicherungsordner
INPUT_DIR = Path(r"C:\Users\rsonnen\Desktop\Sicherung")

# Unterstützte Dateierweiterungen: nur PDF
SUPPORTED_EXT = {".pdf"}

def extract_text_from_file(path: Path) -> str:
    elements = partition(str(path))
    texts = [el.text for el in elements if isinstance(el, NarrativeText) and el.text]
    return "\n".join(texts)


def ingest_folder(folder: Path):
    folder = folder.expanduser().resolve()
    print(f"[Ingest] Scanning {folder}")

    with get_session() as session:
        for p in folder.rglob("*"):
            if p.suffix.lower() in SUPPORTED_EXT and p.is_file():
                if session.query(Document).filter_by(path=str(p)).first():
                    continue
                try:
                    text = extract_text_from_file(p)
                except Exception as e:
                    print(f"[Ingest] Failed {p}: {e}")
                    continue
                session.add(Document(path=str(p), content=text))

        session.commit()
    print("[Ingest] Done.")
