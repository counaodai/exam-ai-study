from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_documents: int = 0
    total_questions: int = 0
    total_conversations: int = 0
    total_methods: int = 0
    method_coverage: float = 0.0


class ModuleStats(BaseModel):
    module_name: str
    question_count: int = 0
    avg_mastery: float = 0.0


class SubModuleStats(BaseModel):
    module_name: str
    sub_module_name: str
    question_count: int = 0
    avg_mastery: float = 0.0


class TrendData(BaseModel):
    date: str
    count: int = 0


class WeakPointStats(BaseModel):
    module_name: str
    sub_module_name: str
    question_count: int = 0
    avg_mastery: float = 0.0


class MethodCoverageStats(BaseModel):
    total_sub_modules: int = 0
    covered_sub_modules: int = 0
    coverage_rate: float = 0.0