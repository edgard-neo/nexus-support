from dotenv import load_dotenv

load_dotenv()

import gradio as gr
from fastapi import FastAPI

from app.api.v1.chat import router as chat_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.api_debug,
)
app.include_router(chat_router, prefix="/api/v1")


def gradio_chat(message: str, history: list, session_id: str) -> str:
    # Chama o agente diretamente — funciona local e no HF Spaces
    from app.agent import agent as agent_module
    from app.security.safety import (
        blocked_response,
        validate_message,
        validate_session_id,
    )

    sid = session_id.strip() or "gradio_user"

    ok, reason = validate_session_id(sid)
    if not ok:
        return blocked_response(reason)

    ok, reason = validate_message(message)
    if not ok:
        return blocked_response(reason)

    try:
        response_text, escalated = agent_module.invoke(
            message=message,
            session_id=sid,
        )
    except Exception as exc:
        logger.error("Erro no agente via Gradio", extra={"error": str(exc)})
        return "Erro interno. Tente novamente."

    if escalated:
        response_text += "\n\n[Atendimento transferido para um especialista]"

    return response_text


with gr.Blocks(title="NexusSupport") as gradio_app:
    gr.Markdown("# NexusSupport\nSuporte ao cliente NexusStore")

    session_id_input = gr.Textbox(
        value="user_001",
        label="Session ID",
        placeholder="Identificador da sessao",
    )
    gr.ChatInterface(
        fn=gradio_chat,
        additional_inputs=[session_id_input],
        examples=[
            ["Qual o status do meu pedido #4521?"],
            ["Qual o prazo de entrega para o interior?"],
            ["Como faco uma devolucao?"],
            ["Quais formas de pagamento voces aceitam?"],
        ],
    )

app = gr.mount_gradio_app(app, gradio_app, path="/")

logger.info("NexusSupport iniciado", extra={"version": settings.api_version})
