"""
Rerank 重排序模块

在向量检索（粗排）之后，使用 Cross-Encoder 模型对候选文档进行精排，
提升检索结果与用户问题的相关性。
通过 SiliconFlow 的 OpenAI 兼容 Rerank API 调用。
"""
import asyncio
import logging
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

RERANK_TIMEOUT = 15  # Rerank API 超时时间（秒）


async def rerank(
    query: str,
    documents: list[dict],
    top_n: int = 3,
) -> list[dict]:
    """
    对候选文档进行重排序

    Args:
        query: 用户查询文本
        documents: 候选文档列表，每个文档需包含 "content" 字段
        top_n: 返回前 N 个最相关文档

    Returns:
        重排序后的文档列表（按相关性降序），附带 rerank_score
    """
    if not documents:
        return []

    if not settings.RERANK_ENABLED:
        logger.debug("Rerank 已禁用，跳过重排序")
        return documents[:top_n]

    # 提取文档内容
    doc_texts = [doc.get("content", "") for doc in documents]

    try:
        rerank_results = await _call_rerank_api(query, doc_texts, top_n)
        return _apply_rerank_results(documents, rerank_results)
    except asyncio.TimeoutError:
        logger.warning(f"Rerank API 超时（{RERANK_TIMEOUT}s），回退到原始排序")
        return documents[:top_n]
    except Exception as e:
        logger.warning(f"Rerank 失败: {e}，回退到原始排序")
        return documents[:top_n]


async def _call_rerank_api(
    query: str,
    documents: list[str],
    top_n: int,
) -> list[dict]:
    """调用 SiliconFlow Rerank API"""
    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/rerank"

    payload = {
        "model": settings.RERANK_MODEL,
        "query": query,
        "documents": documents,
        "top_n": top_n,
    }

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=RERANK_TIMEOUT) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    results = data.get("results", [])
    logger.info(f"Rerank 完成，模型: {settings.RERANK_MODEL}，返回 {len(results)} 条结果")
    return results


def _apply_rerank_results(
    documents: list[dict],
    rerank_results: list[dict],
) -> list[dict]:
    """将 Rerank 结果应用到原始文档列表"""
    reranked = []
    for item in rerank_results:
        idx = item.get("index", 0)
        score = item.get("relevance_score", 0.0)
        if idx < len(documents):
            doc = dict(documents[idx])
            doc["rerank_score"] = round(score, 4)
            doc["score"] = round(score, 4)  # 用 rerank 分数覆盖原始向量相似度
            reranked.append(doc)

    return reranked
