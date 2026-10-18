from fastapi import APIRouter, HTTPException

from app.api.schemas import ChatRequest, ChatResponse
from app.core.logging import get_logger
from app.security.pii import mask_pii
from app.security.safety import blocked_response, validate_message, validate_session_id

router = APIRouter()
logger = get_logger(__name__)


def invoke_agent(message: str, session_id: str) -> tuple[str, bool]:
    from app.agent import agent as agent_module

    return agent_module.invoke(message=message, session_id=session_id)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    # Valida session_id
    ok, reason = validate_session_id(request.session_id)
    if not ok:
        raise HTTPException(status_code=400, detail=blocked_response(reason))

    # Valida mensagem contra prompt injection e tamanho
    ok, reason = validate_message(request.message)
    if not ok:
        return ChatResponse(
            response=blocked_response(reason),
            escalated=False,
            session_id=request.session_id,
        )

    logger.info("Mensagem recebida", extra={"session_id": request.session_id})

    try:
        response_text, escalated = invoke_agent(
            message=request.message,
            session_id=request.session_id,
        )
    except Exception as exc:
        logger.error("Erro no agente", extra={"error": str(exc)})
        raise HTTPException(status_code=500, detail="Erro interno. Tente novamente.")

    # Mascara PII na resposta antes de logar (nunca loga dados reais)
    logger.info(
        "Resposta enviada",
        extra={
            "session_id": request.session_id,
            "escalated": escalated,
            "response_preview": mask_pii(response_text[:100]),
        },
    )

    return ChatResponse(
        response=response_text,
        escalated=escalated,
        session_id=request.session_id,
    )


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}
