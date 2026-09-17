from fastapi import APIRouter

from app.schemas.chat import ChatRequest
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

rag_service = RAGService()


@router.post("/")
def chat(request: ChatRequest) -> dict[str, str]:
    answer = rag_service.answer(
        conversation_id=request.conversation_id,
        question=request.question,
    )

    return {
        "answer": answer
    }