from app.agent.tools.handoff import ESCALATION_SIGNAL, escalar_para_humano


def test_escalacao_contem_sinal():
    result = escalar_para_humano.invoke({"motivo": "cliente solicitou"})
    assert ESCALATION_SIGNAL in result


def test_escalacao_contem_mensagem_ao_usuario():
    result = escalar_para_humano.invoke({"motivo": "cliente solicitou"})
    assert "especialista" in result or "atendente" in result


def test_escalacao_contem_motivo():
    result = escalar_para_humano.invoke({"motivo": "reembolso acima de R$500"})
    assert "reembolso acima de R$500" in result
