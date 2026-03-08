"""
Mascara PII em logs e respostas da API.
Dentro do agente, o PIIMiddleware do LangChain cuida disso automaticamente.
Este modulo e usado apenas fora do fluxo do agente.
"""

import re

# Ordem importa: cartao antes de telefone (ambos tem sequencias numericas longas)
_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    (
        "cartao",
        re.compile(r"\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}"),
        "[CARTAO OCULTADO]",
    ),
    ("cpf", re.compile(r"\d{3}\.?\d{3}\.?\d{3}[\-]?\d{2}"), "[CPF OCULTADO]"),
    (
        "email",
        re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
        "[EMAIL OCULTADO]",
    ),
    (
        "telefone",
        re.compile(r"(?:\+55[\s]?)?(?:\(?\d{2}\)?[\s\-]?)(?:9[\s]?)?\d{4}[\s\-]?\d{4}"),
        "[TELEFONE OCULTADO]",
    ),
    ("cep", re.compile(r"\d{5}[\-]?\d{3}"), "[CEP OCULTADO]"),
]


def mask_pii(text: str) -> str:
    for _name, pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text
