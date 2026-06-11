from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, case, and_, or_
from sqlalchemy.orm import aliased
from app.db.database import get_db
from app.models.document import Document
from app.models.question import Question
from app.models.conversation import Conversation
from app.models.method import MethodSummary
from app.models.module import Module
from app.schemas.analysis import (
    OverviewStats,
    ModuleStats,
    SubModuleStats,
    TrendData,
    WeakPointStats,
    MethodCoverageStats,
)

router = APIRouter(prefix="/analysis", tags=["统计分析"])


@router.get("/overview", response_model=OverviewStats)
async def get_overview(db: AsyncSession = Depends(get_db)):
    doc_count = await db.scalar(select(func.count(Document.id)))
    question_count = await db.scalar(
        select(func.count(Question.id)).where(Question.is_valid == True)
    )
    conv_count = await db.scalar(select(func.count(Conversation.id)))
    method_count = await db.scalar(select(func.count(MethodSummary.id)))

    total_sub_modules = await db.scalar(
        select(func.count(Module.id)).where(Module.level == 2)
    )
    covered_sub_modules = await db.scalar(
        select(func.count(func.distinct(MethodSummary.module_id)))
    )

    coverage_rate = 0.0
    if total_sub_modules and total_sub_modules > 0:
        coverage_rate = round((covered_sub_modules or 0) / total_sub_modules * 100, 1)

    return OverviewStats(
        total_documents=doc_count or 0,
        total_questions=question_count or 0,
        total_conversations=conv_count or 0,
        total_methods=method_count or 0,
        method_coverage=coverage_rate,
    )


@router.get("/modules", response_model=list[ModuleStats])
async def get_module_stats(db: AsyncSession = Depends(get_db)):
    query = (
        select(
            Module.name.label("module_name"),
            func.count(Question.id).label("question_count"),
            func.coalesce(func.avg(Question.mastery), 0).label("avg_mastery"),
        )
        .join(Question, Question.module_id == Module.id, isouter=True)
        .where(
            Module.level == 1,
            or_(Question.id.is_(None), Question.is_valid == True),
        )
        .group_by(Module.id, Module.name)
        .order_by(func.count(Question.id).desc())
    )
    result = await db.execute(query)
    rows = result.all()

    return [
        ModuleStats(
            module_name=row.module_name,
            question_count=row.question_count,
            avg_mastery=round(float(row.avg_mastery), 1),
        )
        for row in rows
    ]


@router.get("/sub-modules", response_model=list[SubModuleStats])
async def get_sub_module_stats(
    module_name: str = None,
    db: AsyncSession = Depends(get_db),
):
    parent = aliased(Module)
    query = (
        select(
            parent.name.label("module_name"),
            Module.name.label("sub_module_name"),
            func.count(Question.id).label("question_count"),
            func.coalesce(func.avg(Question.mastery), 0).label("avg_mastery"),
        )
        .join(parent, Module.parent_id == parent.id)
        .join(Question, Question.module_id == Module.id, isouter=True)
        .where(
            Module.level == 2,
            or_(Question.id.is_(None), Question.is_valid == True),
        )
    )

    if module_name:
        query = query.where(parent.name == module_name)

    query = query.group_by(
        parent.name, Module.id, Module.name
    ).order_by(func.count(Question.id).desc())

    result = await db.execute(query)
    rows = result.all()

    return [
        SubModuleStats(
            module_name=row.module_name,
            sub_module_name=row.sub_module_name,
            question_count=row.question_count,
            avg_mastery=round(float(row.avg_mastery), 1),
        )
        for row in rows
    ]


@router.get("/trends", response_model=list[TrendData])
async def get_trends(days: int = 30, db: AsyncSession = Depends(get_db)):
    start_date = datetime.now() - timedelta(days=days)

    query = (
        select(
            func.date(Question.created_at).label("date"),
            func.count(Question.id).label("count"),
        )
        .where(Question.created_at >= start_date, Question.is_valid == True)
        .group_by(func.date(Question.created_at))
        .order_by(func.date(Question.created_at))
    )

    result = await db.execute(query)
    rows = result.all()

    date_count_map = {str(row.date): row.count for row in rows}

    trend_data = []
    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        trend_data.append(
            TrendData(date=date, count=date_count_map.get(date, 0))
        )

    return trend_data


@router.get("/weak-points", response_model=list[WeakPointStats])
async def get_weak_points(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    parent = aliased(Module)
    query = (
        select(
            parent.name.label("module_name"),
            Module.name.label("sub_module_name"),
            func.count(Question.id).label("question_count"),
            func.coalesce(func.avg(Question.mastery), 0).label("avg_mastery"),
        )
        .join(parent, Module.parent_id == parent.id)
        .join(Question, Question.module_id == Module.id)
        .where(Module.level == 2, Question.is_valid == True)
        .group_by(parent.name, Module.id, Module.name)
        .having(func.count(Question.id) > 0)
        .order_by(func.coalesce(func.avg(Question.mastery), 0))
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        WeakPointStats(
            module_name=row.module_name,
            sub_module_name=row.sub_module_name,
            question_count=row.question_count,
            avg_mastery=round(float(row.avg_mastery), 1),
        )
        for row in rows
    ]


@router.get("/method-coverage", response_model=MethodCoverageStats)
async def get_method_coverage(db: AsyncSession = Depends(get_db)):
    total_sub_modules = await db.scalar(
        select(func.count(Module.id)).where(Module.level == 2)
    )

    covered_sub_modules = await db.scalar(
        select(func.count(func.distinct(MethodSummary.module_id)))
    )

    coverage_rate = 0.0
    if total_sub_modules and total_sub_modules > 0:
        coverage_rate = round((covered_sub_modules or 0) / total_sub_modules * 100, 1)

    return MethodCoverageStats(
        total_sub_modules=total_sub_modules or 0,
        covered_sub_modules=covered_sub_modules or 0,
        coverage_rate=coverage_rate,
    )