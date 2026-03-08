from langchain.tools import tool

# Sinal especial que o endpoint /chat le para setar escalated: true na resposta
ESCALATION_SIGNAL = "__ESCALATED__"


@tool
def escalar_para_humano(motivo: str) -> str:
    """
    Transfere o atendimento para um agente humano.
    Use quando: o cliente pedir explicitamente, houver suspeita de fraude,
    o reembolso for acima de R$500, o cliente estiver irritado,
    ou voce nao conseguir resolver apos duas tentativas.
    """
    return (
        f"{ESCALATION_SIGNAL} "
        f"Entendo a sua situacao. Vou transferir seu atendimento para um de "
        f"nossos especialistas agora. Em breve um atendente entrara em contato. "
        f"Motivo interno: {motivo}"
    )
