import asyncio
import logging
from typing import AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.core.rag.vector_store import search_similar
from app.core.rag.reranker import rerank
from app.prompts.chat import RAG_PROMPT_TEMPLATE, DIRECT_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

RAG_TIMEOUT = 30
LLM_TIMEOUT = 60
STREAM_LLM_TIMEOUT = 120


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=0.3,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_BASE_URL,
    )


def _format_docs(docs: list) -> str:
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.get("source", "未知来源")
        page = doc.get("page", "")
        page_info = f"，第{page}页" if page else ""
        formatted.append(f"【片段{i}】(来源: {source}{page_info})\n{doc.get('content', '')}")
    return "\n\n".join(formatted)


async def _search_with_timeout(question: str, k: int | None = None) -> list:
    if k is None:
        k = settings.RERANK_TOP_K if settings.RERANK_ENABLED else 5
    loop = asyncio.get_event_loop()
    try:
        sources = await asyncio.wait_for(
            loop.run_in_executor(None, search_similar, question, k),
            timeout=RAG_TIMEOUT,
        )
        return sources
    except asyncio.TimeoutError:
        logger.warning(f"RAG 检索超时（{RAG_TIMEOUT}s）")
        return []
    except Exception as e:
        logger.warning(f"RAG 检索失败: {e}")
        return []


async def _search_and_rerank(question: str) -> list:
    """向量检索 + Rerank 精排，返回最终文档列表"""
    # 粗排：向量检索取更多候选
    sources = await _search_with_timeout(question)
    if not sources:
        return []

    # 精排：Rerank 重排序
    if settings.RERANK_ENABLED:
        reranked = await rerank(question, sources, top_n=settings.RERANK_TOP_N)
        if reranked:
            logger.info(
                f"Rerank 完成: {len(sources)} 条候选 → {len(reranked)} 条精排结果"
            )
            return reranked
        logger.warning("Rerank 返回空结果，回退到原始排序")

    return sources[:5]


async def _generate_with_rag(question: str, sources: list) -> str:
    context = _format_docs(sources)
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    llm = get_llm()
    chain = prompt | llm | StrOutputParser()
    return await chain.ainvoke({"context": context, "question": question})


async def _generate_direct(question: str) -> str:
    prompt = ChatPromptTemplate.from_template(DIRECT_PROMPT_TEMPLATE)
    llm = get_llm()
    chain = prompt | llm | StrOutputParser()
    return await chain.ainvoke({"question": question})


async def rag_query(question: str, k: int = 5) -> dict:
    sources = await _search_and_rerank(question)

    try:
        if sources:
            answer = await asyncio.wait_for(
                _generate_with_rag(question, sources),
                timeout=LLM_TIMEOUT,
            )
        else:
            answer = await asyncio.wait_for(
                _generate_direct(question),
                timeout=LLM_TIMEOUT,
            )
        return {"answer": answer, "sources": sources}
    except asyncio.TimeoutError:
        logger.error(f"LLM 生成超时（{LLM_TIMEOUT}s）")
        raise
    except Exception as e:
        logger.error(f"RAG 查询失败: {e}")
        raise


async def rag_query_stream(question: str, sources: list) -> AsyncGenerator[str, None]:
    """流式 RAG 查询，逐块返回 LLM 生成的文本"""
    try:
        if sources:
            context = _format_docs(sources)
            prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
            llm = get_llm()
            chain = prompt | llm | StrOutputParser()
            async for chunk in chain.astream({"context": context, "question": question}):
                if chunk:
                    yield chunk
        else:
            prompt = ChatPromptTemplate.from_template(DIRECT_PROMPT_TEMPLATE)
            llm = get_llm()
            chain = prompt | llm | StrOutputParser()
            async for chunk in chain.astream({"question": question}):
                if chunk:
                    yield chunk
    except asyncio.CancelledError:
        logger.info("流式生成被客户端取消")
        raise
    except Exception as e:
        logger.error(f"流式 RAG 生成失败: {e}")
        raise
