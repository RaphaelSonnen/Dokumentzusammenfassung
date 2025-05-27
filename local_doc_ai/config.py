import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_PATH      = os.getenv("DOC_AI_DB", BASE_DIR / "doc_ai.sqlite")
VECTOR_DIR   = os.getenv("VECTOR_DIR", BASE_DIR / "vector_store")
EMBEDDING_MODEL = os.getenv("EMBED_MODEL", "jina-embeddings-v2-base-de")
JINA_API_KEY = os.getenv("JINA_API_KEY")          # kann leer sein

LLM_MODEL    = os.getenv("LLM_MODEL", "gemma3:27b")   # Ollama-Tag
CHUNK_SIZE   = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
TOP_K        = int(os.getenv("TOP_K", 4))

# ────────── Globaler System-Prompt (Deutsch) ──────────
SYSTEM_PROMPT_DE = (
    "Du bist ein hilfreicher Assistent für interne Projektunterlagen eines "
    "Ingenieurbüros. Antworte **immer ausschließlich auf Deutsch**, nutze kurze, "
    "prägnante Formulierungen. Quellenliste am Ende unter der Überschrift "
    "»Quellen:«."
)
