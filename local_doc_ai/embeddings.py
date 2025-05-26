from langchain_community.embeddings import JinaEmbeddings
from functools import lru_cache
from .config import EMBEDDING_MODEL, JINA_API_KEY

@lru_cache(maxsize=1)
def load_embedder():
    return JinaEmbeddings(
        model_name=EMBEDDING_MODEL,
        jina_api_key=JINA_API_KEY  # can be None for HF offline use
    )

def embed_texts(texts):
    model = load_embedder()
    return model.embed_documents(texts)
