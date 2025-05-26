from chromadb import PersistentClient
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import Document as LIDocument
from .database import Document, get_session
from .embeddings import embed_texts
from .config import VECTOR_DIR, CHUNK_SIZE, CHUNK_OVERLAP

# ─── Embedding ────────────────────────────────────────────────────────────

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


# Embed-Modell einmal global registrieren
Settings.embed_model = LocalEmbedding()

# ─── Parser ───────────────────────────────────────────────────────────────
node_parser = SimpleNodeParser.from_defaults(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)

# ─── Build / Update ───────────────────────────────────────────────────────
def build_vector_index():
    client = PersistentClient(path=str(VECTOR_DIR))
    collection = client.get_or_create_collection("docs")
    chroma_store = ChromaVectorStore(chroma_collection=collection)

    index = VectorStoreIndex.from_vector_store(
        vector_store=chroma_store,
        settings=Settings,
    )

    print("[Index] Loading documents from DB …")
    with get_session() as session:
        docs = session.query(Document).all()
        nodes = []
        for d in docs:
            for node in node_parser.get_nodes_from_documents(
                [LIDocument(text=d.content, metadata={"path": d.path})]
            ):
                node.metadata["doc_path"] = d.path
                nodes.append(node)

        if nodes:
            print(f"[Index] Adding {len(nodes)} nodes …")
            try:
                index.insert_nodes(nodes)
            except Exception as e:
                print(f"[Index] insert_nodes failed: {e}")

    print("[Index] Build complete.")
