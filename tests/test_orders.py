from app.agent.tools.orders import buscar_pedido


def test_pedido_existente():
    result = buscar_pedido.invoke({"numero_pedido": "4521"})
    assert "4521" in result
    assert "transito" in result


def test_pedido_com_hash():
    # Usuario digita "#4521" — o tool deve tratar o prefixo
    result = buscar_pedido.invoke({"numero_pedido": "#4521"})
    assert "4521" in result
    assert "nao encontrado" not in result


def test_pedido_entregue():
    result = buscar_pedido.invoke({"numero_pedido": "4522"})
    assert "entregue" in result


def test_pedido_cancelado():
    result = buscar_pedido.invoke({"numero_pedido": "4525"})
    assert "cancelado" in result


def test_pedido_nao_encontrado():
    result = buscar_pedido.invoke({"numero_pedido": "9999"})
    assert "nao encontrado" in result


def test_pedido_com_rastreio():
    result = buscar_pedido.invoke({"numero_pedido": "4521"})
    assert "BR123456789BR" in result


def test_pedido_sem_rastreio():
    # Pedido em separacao ainda nao tem codigo de rastreio
    result = buscar_pedido.invoke({"numero_pedido": "4524"})
    assert "rastreio" not in result.lower() or "None" not in result
