import os
import sqlite3
from functools import lru_cache
from pathlib import Path

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.sqlite import SqliteSaver

from app.agent.tools.faq_retriever import buscar_faq
from app.agent.tools.handoff import escalar_para_humano
from app.agent.tools.orders import buscar_pedido
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_CPF_REGEX = r"\d{3}\.?\d{3}\.?\d{3}[\-]?\d{2}"
_TELEFONE_BR_REGEX = r"(?:\+55[\s]?)?(?:\(?\d{2}\)?[\s\-]?)(?:9[\s]?)?\d{4}[\s\-]?\d{4}"


def _load_system_prompt() -> str:
    path = settings.system_prompt_path
    if path.exists():
        return path.read_text(encoding="utf-8")
    logger.warning("system.md nao encontrado, usando prompt padrao")
    return "Voce e um agente de suporte ao cliente. Seja util e direto."


def _build_checkpointer() -> SqliteSaver:
    db_path = (PROJECT_ROOT / settings.sqlite_db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    return SqliteSaver(conn)


@lru_cache(maxsize=1)
def get_agent():
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY não configurada")

    if settings.langchain_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project

    model = init_chat_model(
        model=settings.groq_model,
        model_provider="groq",
        temperature=settings.groq_temperature,
        max_tokens=settings.groq_max_tokens,
    )

    middleware = [
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="redact", apply_to_input=True),
        PIIMiddleware(
            "cpf", detector=_CPF_REGEX, strategy="redact", apply_to_input=True
        ),
        PIIMiddleware(
            "telefone",
            detector=_TELEFONE_BR_REGEX,
            strategy="redact",
            apply_to_input=True,
        ),
    ]

    agent = create_agent(
        model=model,
        tools=[buscar_pedido, buscar_faq, escalar_para_humano],
        system_prompt=_load_system_prompt(),
        checkpointer=_build_checkpointer(),
        middleware=middleware,
    )

    logger.info("Agente inicializado", extra={"model": settings.groq_model})
    return agent


def invoke(message: str, session_id: str) -> tuple[str, bool]:
    agent = get_agent()

    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        {"configurable": {"thread_id": session_id}},
    )

    last_message = result["messages"][-1]
    response_text: str = (
        last_message.content or "Desculpe, nao consegui processar sua mensagem."
    )

    from app.agent.tools.handoff import ESCALATION_SIGNAL

    escalated = ESCALATION_SIGNAL in response_text

    if escalated:
        response_text = response_text.replace(ESCALATION_SIGNAL, "").strip()

    return response_text, escalated
