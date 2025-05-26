import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = os.getenv("DOC_AI_DB", BASE_DIR / "doc_ai.sqlite")
VECTOR_DIR = os.getenv("VECTOR_DIR", BASE_DIR / "vector_store")
EMBEDDING_MODEL = os.getenv(
    "EMBED_MODEL",
    "jina-embeddings-v2-base-de"  # 768-d bilingual DE-EN
)
JINA_API_KEY = os.getenv("jina_6b29f412d4bd418c9b870526ae53ada9ZTxj91aqDtXsKWXLSDpR0D7B5WSv")      # new

LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:27b")  # Ollama model tag
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
TOP_K = int(os.getenv("TOP_K", 4))  # num context chunks for retrieval
