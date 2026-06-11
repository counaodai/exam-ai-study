from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.mindmaps import router as mindmaps_router
from app.api.analysis import router as analysis_router
from app.api.methods import router as methods_router
from app.api.modules import router as modules_router
from app.api.classify import router as classify_router
from app.api.cleanup import router as cleanup_router
from app.api.questions import router as questions_router

__all__ = [
    "documents_router",
    "chat_router",
    "mindmaps_router",
    "analysis_router",
    "methods_router",
    "modules_router",
    "classify_router",
    "cleanup_router",
    "questions_router",
]
