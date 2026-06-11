import logging
from pathlib import Path
import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import settings
from app.core.rag.embedder import get_embeddings
from app.schemas.document import DocumentChunk

logger = logging.getLogger(__name__)

COLLECTION_NAME = "exam_knowledge"
CHROMA_PERSIST_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "chroma_data")

_chroma_client: chromadb.ClientAPI | None = None
_vector_store: Chroma | None = None


def _get_chroma_client() -> chromadb.ClientAPI:
    global _chroma_client
    if _chroma_client is None:
        if settings.CHROMA_HOST != "localhost" or settings.CHROMA_PORT != 8000:
            try:
                _chroma_client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT,
                )
                _chroma_client.heartbeat()
                logger.info(f"连接远程 ChromaDB: {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
            except Exception as e:
                logger.warning(f"远程 ChromaDB 连接失败: {e}，使用本地持久化模式")
                Path(CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
                _chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        else:
            Path(CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
            _chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
            logger.info(f"使用本地 ChromaDB 持久化模式: {CHROMA_PERSIST_DIR}")
    return _chroma_client


def get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        client = _get_chroma_client()
        embeddings = get_embeddings()
        _vector_store = Chroma(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
        )
        logger.info(f"初始化向量数据库，集合: {COLLECTION_NAME}")
    return _vector_store


def _chunk_to_langchain_doc(chunk: DocumentChunk) -> Document:
    metadata = {
        "source": chunk.source,
        "module": chunk.module or "",
        "chunk_type": chunk.chunk_type.value,
        "page": chunk.metadata.page or 0,
        "chapter": chunk.metadata.chapter or "",
        "question_number": chunk.metadata.question_number or 0,
        "year": chunk.metadata.year or "",
        "tags": ",".join(chunk.metadata.tags),
    }
    return Document(
        page_content=chunk.content,
        metadata=metadata,
        id=chunk.id,
    )


def add_chunks(chunks: list[DocumentChunk]) -> int:
    if not chunks:
        return 0

    store = get_vector_store()
    documents = [_chunk_to_langchain_doc(c) for c in chunks]
    ids = [c.id for c in chunks]

    batch_size = 100
    added = 0
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        store.add_documents(documents=batch_docs, ids=batch_ids)
        added += len(batch_docs)

    logger.info(f"成功写入 {added} 个分块到向量数据库")
    return added


def delete_by_source(source: str) -> int:
    store = get_vector_store()
    collection = store._collection
    results = collection.get(where={"source": source})
    if results and results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info(f"已删除来源 [{source}] 的 {len(results['ids'])} 个向量")
        return len(results["ids"])
    return 0


def search_similar(query: str, k: int = 5) -> list[dict]:
    store = get_vector_store()
    results = store.similarity_search_with_score(query, k=k)

    formatted = []
    for doc, score in results:
        formatted.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", ""),
            "module": doc.metadata.get("module", ""),
            "chunk_type": doc.metadata.get("chunk_type", ""),
            "page": doc.metadata.get("page", 0),
            "chapter": doc.metadata.get("chapter", ""),
            "score": round(1 - score, 4),
        })

    return formatted
