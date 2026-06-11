import uuid
import json
import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.conversation import Conversation, Message
from app.models.module import Module
from app.models.question import Question
from app.schemas.chat import (
    SendMessageRequest,
    ChatMessageResponse,
    ConversationResponse,
    ConversationDetailResponse,
    ClassificationResult,
    MindMapUpdateResult,
    UpdateClassificationRequest,
    SourceItem,
)
from app.core.rag.retriever import rag_query, rag_query_stream, _search_and_rerank
from app.core.ai.classifier import classify_question
from app.core.ai.question_validator import validate_question
from app.core.mindmap.updater import update_mindmap_after_classification
from app.core.ai.method_extract import extract_method
from app.models.method import MethodSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI问答"])


async def _find_module_id(
    db: AsyncSession,
    primary_module: str,
    secondary_module: str | None,
) -> uuid.UUID | None:
    if secondary_module:
        parent_query = select(Module).where(
            Module.name == primary_module,
            Module.level == 1,
        )
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()
        if not parent:
            return None
        query = select(Module).where(
            Module.name == secondary_module,
            Module.level == 2,
            Module.parent_id == parent.id,
        )
    else:
        query = select(Module).where(
            Module.name == primary_module,
            Module.level == 1,
        )

    result = await db.execute(query)
    module = result.scalar_one_or_none()
    return module.id if module else None


async def _post_process_classification(
    msg_id: str,
    question_text: str,
):
    """后台任务：校验 + 分类 + 思维导图更新 + 方法论生成"""
    from app.db.database import async_session

    try:
        async with async_session() as db:
            # ========== 第零步：提问有效性校验 ==========
            validation = await validate_question(question_text)
            if not validation.is_valid:
                logger.info(
                    f"无效提问已拦截: msg_id={msg_id}, "
                    f"filter_layer={validation.filter_layer}, "
                    f"reason={validation.reason}"
                )
                # 标记 Message 为无效提问，不进入分类/导图/统计流程
                msg = await db.get(Message, uuid.UUID(msg_id))
                if msg:
                    msg.classification = {
                        "module": "无效提问",
                        "sub_module": "",
                        "confidence": 0.0,
                        "reason": f"[已拦截] {validation.reason}",
                        "is_valid": False,
                    }
                await db.commit()
                return

            # ========== 第一步：分类 ==========
            classify_result = await classify_question(question_text)
            classification = ClassificationResult(
                module=classify_result.primary_module,
                sub_module=classify_result.secondary_module or "",
                confidence=classify_result.confidence,
                reason=classify_result.reason,
            )

            module_id = await _find_module_id(
                db,
                classify_result.primary_module,
                classify_result.secondary_module,
            )

            question_id = None
            if module_id:
                question = Question(
                    content=question_text,
                    module_id=module_id,
                    source="AI问答",
                    mastery=0,
                )
                db.add(question)
                await db.flush()
                question_id = question.id

            mindmap_update = None
            try:
                update_result = await update_mindmap_after_classification(
                    db,
                    classify_result.primary_module,
                    classify_result.secondary_module,
                    question_id=question_id,
                )
                mindmap_update = MindMapUpdateResult(
                    updated=update_result.get("updated", False),
                    mindmap_id=update_result.get("mindmap_id"),
                    node_label=update_result.get("node_label"),
                    question_count=update_result.get("question_count", 0),
                    mastery=update_result.get("mastery", 0),
                    should_generate_method=update_result.get("should_generate_method", False),
                )
            except Exception as e:
                logger.error(f"思维导图更新失败: {e}")

            if mindmap_update and mindmap_update.should_generate_method and module_id:
                try:
                    existing = await db.execute(
                        select(MethodSummary).where(MethodSummary.module_id == module_id)
                    )
                    if not existing.scalar_one_or_none():
                        module = await db.get(Module, module_id)
                        if module:
                            module_name = module.name
                            if module.parent_id:
                                parent = await db.get(Module, module.parent_id)
                                if parent:
                                    module_name = f"{parent.name} > {module.name}"

                            question_query = (
                                select(Question)
                                .where(Question.module_id == module.id)
                                .order_by(Question.created_at.desc())
                                .limit(20)
                            )
                            q_result = await db.execute(question_query)
                            questions = q_result.scalars().all()

                            if len(questions) >= 3:
                                questions_data = [
                                    {"content": q.content, "answer": q.answer or "", "explanation": q.explanation or ""}
                                    for q in questions
                                ]
                                method_result = await extract_method(module_name, questions_data)
                                method = MethodSummary(
                                    module_id=module.id,
                                    method_name=method_result.get("method_name", f"{module.name}解题方法"),
                                    recognition=method_result.get("recognition"),
                                    steps=method_result.get("steps", []),
                                    traps=method_result.get("traps"),
                                    quick_tips=method_result.get("quick_tips"),
                                    key_formulas=method_result.get("key_formulas"),
                                    summary=method_result.get("summary"),
                                    question_count=len(questions),
                                    source_question_ids=[str(q.id) for q in questions],
                                    is_auto_generated=True,
                                )
                                db.add(method)
                                logger.info(f"自动方法论生成: {method.method_name}")
                except Exception as e:
                    logger.error(f"自动方法论生成失败: {e}")

            msg = await db.get(Message, uuid.UUID(msg_id))
            if msg:
                msg.classification = classification.model_dump()
                msg.module_id = module_id

            await db.commit()
            logger.info(f"后台分类完成: msg_id={msg_id}, module={classify_result.primary_module}")

    except Exception as e:
        logger.error(f"后台分类任务失败: {e}")


def _build_message_response(
    msg: Message,
    classification: ClassificationResult | None = None,
    sources: list | None = None,
    mindmap_update: MindMapUpdateResult | None = None,
) -> ChatMessageResponse:
    source_items = None
    if sources:
        source_items = [SourceItem(**s) if isinstance(s, dict) else s for s in sources]
    elif msg.sources:
        source_items = [SourceItem(**s) if isinstance(s, dict) else s for s in msg.sources]

    cls = classification
    if not cls and msg.classification:
        cls = ClassificationResult(**msg.classification)

    return ChatMessageResponse(
        id=str(msg.id),
        conversation_id=str(msg.conversation_id),
        role=msg.role,
        content=msg.content,
        question_id=str(msg.question_id) if msg.question_id else None,
        module_id=str(msg.module_id) if msg.module_id else None,
        classification=cls,
        sources=source_items,
        mindmap_update=mindmap_update,
        created_at=msg.created_at,
    )


@router.post("", response_model=ChatMessageResponse)
async def send_message(
    request: SendMessageRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    if request.conversation_id:
        conv = await db.get(Conversation, uuid.UUID(request.conversation_id))
        if not conv:
            raise HTTPException(status_code=404, detail="对话不存在")
    else:
        title = request.content[:50] + ("..." if len(request.content) > 50 else "")
        conv = Conversation(title=title)
        db.add(conv)
        await db.flush()

    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=request.content,
    )
    db.add(user_msg)
    await db.flush()

    try:
        rag_result = await rag_query(request.content)
        ai_content = rag_result.get("answer", "抱歉，暂时无法生成回答。")
        sources = rag_result.get("sources", [])
    except Exception as e:
        logger.error(f"RAG 查询失败: {e}")
        ai_content = "⚠️ AI 服务暂时不可用，请稍后重试。"
        sources = []

    ai_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=ai_content,
        sources=sources if sources else None,
    )
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    background_tasks.add_task(
        _post_process_classification,
        str(ai_msg.id),
        request.content,
    )

    return _build_message_response(
        ai_msg,
        sources=sources,
    )


def _format_sources_for_stream(sources: list) -> list:
    """将检索结果格式化为前端所需的 sources 格式"""
    formatted = []
    for s in sources:
        formatted.append({
            "content": s.get("content", ""),
            "source": s.get("source", ""),
            "page": s.get("page") or None,
            "score": s.get("similarity", 0.0),
        })
    return formatted


async def _save_stream_result(
    conv_id: str,
    full_answer: str,
    sources: list,
    question_text: str,
):
    """后台任务：保存流式输出的完整回答到数据库，并触发分类"""
    from app.db.database import async_session

    try:
        async with async_session() as db:
            ai_msg = Message(
                conversation_id=uuid.UUID(conv_id),
                role="assistant",
                content=full_answer,
                sources=sources if sources else None,
            )
            db.add(ai_msg)
            await db.commit()
            await db.refresh(ai_msg)
            logger.info(
                f"流式回答已保存: conv_id={conv_id}, msg_id={ai_msg.id}, "
                f"length={len(full_answer)}"
            )
            await _post_process_classification(str(ai_msg.id), question_text)
    except Exception as e:
        logger.error(f"保存流式回答失败: {e}")


@router.post("/stream")
async def stream_message(
    request: SendMessageRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    if request.conversation_id:
        conv = await db.get(Conversation, uuid.UUID(request.conversation_id))
        if not conv:
            raise HTTPException(status_code=404, detail="对话不存在")
    else:
        title = request.content[:50] + ("..." if len(request.content) > 50 else "")
        conv = Conversation(title=title)
        db.add(conv)
        await db.flush()

    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=request.content,
    )
    db.add(user_msg)
    await db.commit()

    conv_id = str(conv.id)
    question_text = request.content

    try:
        sources = await _search_and_rerank(question_text)
    except Exception as e:
        logger.error(f"RAG 检索失败: {e}")
        sources = []

    formatted_sources = _format_sources_for_stream(sources)

    async def generate():
        metadata = {
            "type": "metadata",
            "conversation_id": conv_id,
            "sources": formatted_sources,
        }
        yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"

        full_answer_parts: list[str] = []
        try:
            async for chunk in rag_query_stream(question_text, sources):
                full_answer_parts.append(chunk)
                yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"
        except asyncio.CancelledError:
            logger.info("流式响应被客户端断开")
            raise
        except Exception as e:
            logger.error(f"流式生成异常: {e}")
            error_msg = "⚠️ AI 生成过程中出现错误，已生成的内容已保留。"
            if not full_answer_parts:
                error_msg = "⚠️ AI 服务暂时不可用，请稍后重试。"
            full_answer_parts.append(error_msg)
            yield f"data: {json.dumps({'type': 'content', 'content': error_msg}, ensure_ascii=False)}\n\n"

        full_answer = "".join(full_answer_parts)
        formatted_sources_for_save = sources if sources else None
        background_tasks.add_task(
            _save_stream_result,
            conv_id,
            full_answer,
            formatted_sources_for_save,
            question_text,
        )

        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def get_conversations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation).order_by(Conversation.updated_at.desc())
    )
    return result.scalars().all()


@router.get("/conversations/{conv_id}", response_model=ConversationDetailResponse)
async def get_conversation_detail(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await db.get(Conversation, uuid.UUID(conv_id))
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    msg_responses = [_build_message_response(msg) for msg in messages]
    return ConversationDetailResponse(
        conversation=conv,
        messages=msg_responses,
    )


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await db.get(Conversation, uuid.UUID(conv_id))
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    await db.delete(conv)
    return {"message": "删除成功"}


@router.put("/messages/{msg_id}/classification")
async def update_message_classification(
    msg_id: str,
    request: UpdateClassificationRequest,
    db: AsyncSession = Depends(get_db),
):
    msg = await db.get(Message, uuid.UUID(msg_id))
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")

    module_id = await _find_module_id(db, request.module, request.sub_module or None)

    new_classification = ClassificationResult(
        module=request.module,
        sub_module=request.sub_module or "",
        confidence=1.0,
        reason="用户手动修正",
    )
    msg.classification = new_classification.model_dump()
    msg.module_id = module_id

    mindmap_update = None
    if module_id:
        question = Question(
            content=msg.content,
            module_id=module_id,
            source="AI问答-手动修正",
            mastery=0,
        )
        db.add(question)
        await db.flush()

        update_result = await update_mindmap_after_classification(
            db,
            request.module,
            request.sub_module,
            question_id=question.id,
        )
        mindmap_update = MindMapUpdateResult(
            updated=update_result.get("updated", False),
            mindmap_id=update_result.get("mindmap_id"),
            node_label=update_result.get("node_label"),
            question_count=update_result.get("question_count", 0),
            mastery=update_result.get("mastery", 0),
            should_generate_method=update_result.get("should_generate_method", False),
        )

    await db.commit()
    return {
        "message": "分类修正成功",
        "classification": new_classification.model_dump(),
        "mindmap_update": mindmap_update.model_dump() if mindmap_update else None,
    }
