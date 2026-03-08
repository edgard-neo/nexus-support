# consulta de pedidos
from langchain.tools import tool

# Pedidos mock — em producao isso seria uma chamada ao banco de dados da loja
PEDIDOS: dict[str, dict] = {
    "4521": {
        "status": "em transito",
        "previsao": "2 dias uteis",
        "transportadora": "Correios",
        "rastreio": "BR123456789BR",
    },
    "4522": {
        "status": "entregue",
        "previsao": "entregue em 12/02/2026",
        "transportadora": "Jadlog",
        "rastreio": "JD987654321BR",
    },
    "4523": {
        "status": "aguardando pagamento",
        "previsao": "envio em ate 1 dia apos confirmacao",
        "transportadora": None,
        "rastreio": None,
    },
    "4524": {
        "status": "em separacao",
        "previsao": "envio em 1 dia util",
        "transportadora": "Correios",
        "rastreio": None,
    },
    "4525": {
        "status": "cancelado",
        "previsao": "reembolso em ate 5 dias uteis",
        "transportadora": None,
        "rastreio": None,
    },
}


@tool
def buscar_pedido(numero_pedido: str) -> str:
    """
    Consulta o status de um pedido pelo numero.
    Use quando o usuario mencionar um numero de pedido (ex: #4521, pedido 4521).
    """
    numero = numero_pedido.strip().lstrip("#")
    pedido = PEDIDOS.get(numero)

    if not pedido:
        return f"Pedido #{numero} nao encontrado. Verifique o numero e tente novamente."

    status = pedido["status"]
    previsao = pedido["previsao"]
    rastreio = pedido.get("rastreio")

    resposta = f"Pedido #{numero}: {status}. Previsao: {previsao}."
    if rastreio:
        resposta += f" Codigo de rastreio: {rastreio}."

    return resposta
