import uuid
import os
import logging
import asyncio
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db, async_session
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentChunk
from app.config import settings
from app.core.rag.parser import parse_document
from app.core.rag.chunker import smart_chunk
from app.core.rag.vector_store import add_chunks, delete_by_source, search_similar
import aiofiles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["文档管理"])


async def _process_document_background(
    doc_id: str,
    file_path: str,
    file_type: str,
    filename: str,
    module: str | None,
):
    async with async_session() as db:
        try:
            result = await db.execute(select(Document).where(Document.id == uuid.UUID(doc_id)))
            doc = result.scalar_one_or_none()
            if not doc:
                logger.error(f"文档 [{filename}] 未找到记录，doc_id={doc_id}")
                return

            doc.status = "processing"
            await db.commit()
            logger.info(f"文档 [{filename}] 开始处理")

            parsed = await asyncio.to_thread(parse_document, file_path, file_type)
            if not parsed.pages:
                doc.status = "failed"
                await db.commit()
                logger.warning(f"文档 [{filename}] 解析结果为空")
                return

            full_text = parsed.full_text
            chunks = await asyncio.to_thread(
                smart_chunk, full_text, filename, module
            )

            if not chunks:
                doc.status = "failed"
                await db.commit()
                logger.warning(f"文档 [{filename}] 分块结果为空")
                return

            added_count = await asyncio.to_thread(add_chunks, chunks)

            doc.chunk_count = added_count
            doc.status = "completed"
            await db.commit()
            logger.info(f"文档 [{filename}] 处理完成，共 {added_count} 个分块")

        except Exception as e:
            logger.error(f"文档 [{filename}] 处理失败: {e}", exc_info=True)
            try:
                result = await db.execute(select(Document).where(Document.id == uuid.UUID(doc_id)))
                doc = result.scalar_one_or_none()
                if doc:
                    doc.status = "failed"
                    await db.commit()
            except Exception:
                logger.error(f"更新文档 [{filename}] 失败状态时出错", exc_info=True)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    module: str | None = None,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = {".pdf", ".docx", ".doc", ".txt", ".md"}
    if file_ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file_ext}")

    content = await file.read()
    file_size = len(content)

    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制: {settings.MAX_FILE_SIZE_MB}MB",
        )

    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    file_id = str(uuid.uuid4())
    save_path = os.path.join(upload_dir, f"{file_id}{file_ext}")

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    doc = Document(
        filename=file.filename,
        file_type=file_ext.lstrip("."),
        file_size=file_size,
        file_path=save_path,
        module=module,
        status="pending",
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    doc_id_str = str(doc.id)

    background_tasks.add_task(
        _process_document_background,
        doc_id=doc_id_str,
        file_path=save_path,
        file_type=file_ext.lstrip("."),
        filename=file.filename,
        module=module,
    )

    return doc


@router.post("/{doc_id}/reprocess", response_model=DocumentResponse)
async def reprocess_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    result = await db.execute(select(Document).where(Document.id == uuid.UUID(doc_id)))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    if doc.status == "processing":
        raise HTTPException(status_code=400, detail="文档正在处理中，请稍候")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=400, detail="原始文件已丢失，请重新上传")

    doc.status = "pending"
    await db.flush()
    await db.refresh(doc)

    background_tasks.add_task(
        _process_document_background,
        doc_id=str(doc.id),
        file_path=doc.file_path,
        file_type=doc.file_type,
        filename=doc.filename,
        module=doc.module,
    )

    return doc


@router.get("", response_model=list[DocumentResponse])
async def get_document_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == uuid.UUID(doc_id)))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    try:
        delete_by_source(doc.filename)
    except Exception as e:
        logger.warning(f"删除向量数据失败: {e}")

    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
    return {"message": "删除成功"}


@router.get("/{doc_id}/chunks")
async def get_document_chunks(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == uuid.UUID(doc_id)))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    try:
        parsed = await asyncio.to_thread(parse_document, doc.file_path, doc.file_type)
        full_text = parsed.full_text
        chunks = await asyncio.to_thread(smart_chunk, full_text, doc.filename, doc.module)
        return [chunk.model_dump() for chunk in chunks]
    except Exception as e:
        logger.error(f"获取文档分块失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分块失败: {str(e)}")


@router.get("/{doc_id}/status")
async def get_document_status(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == uuid.UUID(doc_id)))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {
        "id": str(doc.id),
        "status": doc.status,
        "chunk_count": doc.chunk_count,
    }
