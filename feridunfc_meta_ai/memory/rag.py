
from __future__ import annotations
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Hafif bir iskelet: chromadb / sentence-transformers opsiyonel.
# Yoksa graceful fallback: boş string döner.

_RAG_READY = False
try:
    import chromadb  # type: ignore
    from sentence_transformers import SentenceTransformer  # type: ignore
    _RAG_READY = True
except Exception:
    _RAG_READY = False

_chroma_client = None
_embedding_model = None
_collection = None

def _ensure_init(workdir: str = ".", collection_name: str = "codebase") -> bool:
    global _chroma_client, _embedding_model, _collection
    if not _RAG_READY:
        return False
    if _chroma_client is None:
        try:
            _chroma_client = chromadb.PersistentClient(path=os.path.join(workdir, ".chroma"))
            _embedding_model = SentenceTransformer(os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"))
            _collection = _chroma_client.get_or_create_collection(name=collection_name, metadata={"hnsw:space":"cosine"})
        except Exception as e:
            logger.warning("RAG init failed: %s", e)
            return False
    return True

async def try_retrieve_context(task: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
    if os.getenv("RAG_ENABLED", "1").strip() != "1":
        return None
    workdir = context.get("workdir", ".")
    if not _ensure_init(workdir):
        return None
    try:
        query = (task.get("description") or task.get("title") or str(task))[:512]
        # Basit arama: en iyi 5 parça
        # Not: sentence-transformers encode sync çalışır; burada sadece demo düzeyi
        vec = _embedding_model.encode([query]).tolist()[0]
        results = _collection.query(query_embeddings=[vec], n_results=5)
        docs = results.get("documents", [[]])[0]
        joined = "\n---\n".join(docs) if docs else None
        return joined
    except Exception as e:
        logger.warning("RAG retrieve failed: %s", e)
        return None

def index_codebase(workdir: str = ".") -> int:
    """Basit indeksleme: .py dosyalarını okuyup Chroma'ya ekler."""
    if not _ensure_init(workdir):
        logger.warning("RAG not ready; install chromadb & sentence-transformers to enable indexing.")
        return 0
    import os, glob, uuid
    paths = [p for p in glob.glob(os.path.join(workdir, "**", "*.py"), recursive=True)]
    docs, ids = [], []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            if not txt.strip():
                continue
            docs.append(txt[:4000])  # naive chunk
            ids.append(str(uuid.uuid4()))
        except Exception:
            continue
    if not docs:
        return 0
    embs = _embedding_model.encode(docs).tolist()
    _collection.add(documents=docs, embeddings=embs, ids=ids, metadatas=[{"path": ""}] * len(docs))
    return len(docs)
