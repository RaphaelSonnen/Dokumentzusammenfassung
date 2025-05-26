import ollama                             # ← bleibt, um Verfügbarkeit zu prüfen
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from chromadb import PersistentClient
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.embeddings import BaseEmbedding
from .config import VECTOR_DIR, LLM_MODEL, TOP_K
from llama_index.llms.ollama import Ollama      # ✔ offizieller Wrapper

from .config import VECTOR_DIR, LLM_MODEL, TOP_K, EMBEDDING_MODEL
from .embeddings import embed_texts


from llama_index.core.embeddings import BaseEmbedding
from .embeddings import embed_texts


class LocalEmbedding(BaseEmbedding):
    def __init__(self):
        self._dim = 768   # Jina v2-base
        super().__init__()

    def _get_text_embedding(self, text: str):
        return embed_texts([text])[0]

    _get_query_embedding = _get_text_embedding
    async def _aget_text_embedding(self, text): return self._get_text_embedding(text)
    async def _aget_query_embedding(self, q):   return self._get_text_embedding(q)

    @property
    def dimension(self): return self._dim




def get_query_engine():
    # 1) Vector-Store laden
    client = PersistentClient(path=str(VECTOR_DIR))
    collection = client.get_or_create_collection("docs")
    vector_store = ChromaVectorStore(chroma_collection=collection)

    # 2) Storage-Context + LLM
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    llm = Ollama(model=LLM_MODEL, request_timeout=120.0)

    # 3) Embed-Modell global registrieren (einmal reicht)
    if Settings.embed_model is None:
        Settings.embed_model = LocalEmbedding()

    # 4) Index ↔ Query-Engine
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        settings=Settings,      # nutzt unser Embed-Modell
    )
    engine = index.as_query_engine(
        llm=llm,                # LLM für Antworten
        similarity_top_k=TOP_K  # wie viele Chunks anhängen
    )
    return engine
