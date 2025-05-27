import ollama
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from chromadb import PersistentClient
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.embeddings import BaseEmbedding
from llama_index.llms.ollama import Ollama 
from .config import VECTOR_DIR, LLM_MODEL, TOP_K, SYSTEM_PROMPT_DE
from .embeddings import embed_texts

# Lokales Embed-Modell (Jina)
class LocalEmbedding(BaseEmbedding):
    def __init__(self):
        self._dim = 768
        super().__init__()

    def _get_text_embedding(self, text: str):
        return embed_texts([text])[0]

    _get_query_embedding = _get_text_embedding
    async def _aget_text_embedding(self, text): return self._get_text_embedding(text)
    async def _aget_query_embedding(self, q):   return self._get_text_embedding(q)

    @property
    def dimension(self): return self._dim


def get_query_engine():
    # Vector-Store
    client = PersistentClient(path=str(VECTOR_DIR))
    collection = client.get_or_create_collection("docs")
    vector_store = ChromaVectorStore(chroma_collection=collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Ollama-LLM mit deutschem System-Prompt
    llm = Ollama(
        model=LLM_MODEL,
        request_timeout=120.0,
        system_prompt=SYSTEM_PROMPT_DE,
    )

    # Embed-Modell global setzen
    if Settings.embed_model is None:
        Settings.embed_model = LocalEmbedding()

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        settings=Settings,
    )

    engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=TOP_K,
    )
    return engine
