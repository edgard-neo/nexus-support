import re

MAX_MESSAGE_LENGTH = 2000
MAX_SESSION_ID_LENGTH = 64

_DIRECT: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions?",
        r"esquece?\s+(todas?\s+)?(as\s+)?instru[çc][õo]es",
        r"jailbreak",
        r"prompt\s*injection",
        r"system\s*prompt\s*(?:leak|reveal|show|print)",
        r"reveal\s+(?:your\s+)?(?:system\s+)?(?:prompt|instructions?)",
        r"<\s*system\s*>",
        r"\[INST\]|\[\/INST\]",
    ]
]

_SUBTLE: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"(novos?|new)\s+(par[âa]metros?|instru[çc][õo]es?|rules?)",
        r"(redefinir?|override|substituir?)\s+(comportamento|behavior|persona)",
        r"modo\s+(desenvolvedor|developer|debug|admin|bypass)",
        r"agora\s+voc[êe]\s+[ée]\s+(?:um?|uma?)\s+\w+",
        r"pretend\s+(you\s+are|to\s+be)",
        r"roleplay\s+as",
    ]
]


def validate_message(text: str) -> tuple[bool, str]:
    """
    Retorna (True, "") se seguro, ou (False, motivo) se bloqueado.
    """
    if not text or not text.strip():
        return False, "empty"

    if len(text) > MAX_MESSAGE_LENGTH:
        return False, "too_long"

    for pattern in _DIRECT + _SUBTLE:
        if pattern.search(text):
            return False, "injection"

    return True, ""


def validate_session_id(session_id: str) -> tuple[bool, str]:
    if not session_id or not session_id.strip():
        return False, "empty"
    if len(session_id) > MAX_SESSION_ID_LENGTH:
        return False, "too_long"
    if not re.match(r"^[a-zA-Z0-9_\-]+$", session_id):
        return False, "invalid_chars"
    return True, ""


def blocked_response(reason: str) -> str:
    if reason == "too_long":
        return f"Mensagem muito longa. Limite: {MAX_MESSAGE_LENGTH} caracteres."
    if reason == "empty":
        return "Nao recebi nenhuma mensagem. Como posso ajudar?"
    return "Nao consigo processar essa mensagem. Tente reformular sua duvida."
