"""Testes das regras de mapeamento.

Dica: monte um ContextoInterpretacao real com uma Voz e uma Partitura
vazias; as regras são pequenas e não precisam de dublês.
"""

import pytest


def test_regra_nota_adiciona_evento_com_parametros_atuais_da_voz():
    pytest.skip("TODO")


def test_regra_nota_sem_duracao_usa_duracao_padrao():
    pytest.skip("TODO")


def test_regra_pausa_adiciona_pausa():
    pytest.skip("TODO")


def test_repetir_ou_pausar_repete_quando_anterior_era_nota():
    """"A:3H" -> duas notas Lá."""
    pytest.skip("TODO")


def test_repetir_ou_pausar_pausa_quando_anterior_nao_era_nota():
    """"aH" -> duas pausas."""
    pytest.skip("TODO")


def test_regra_volume_dobra_volume():
    pytest.skip("TODO")


def test_regra_oitava_sobe_com_interrogacao_e_desce_com_V():
    pytest.skip("TODO")


def test_regra_instrumento_fixo():
    """'!' -> Bandoneon."""
    pytest.skip("TODO")


def test_regra_soma_digito_par():
    """Instrumento 6 + '4' -> 10."""
    pytest.skip("TODO")


def test_regra_andamento_registra_mudanca_na_posicao_atual():
    """"C:3 >" -> MudancaAndamento(posicao=duração de C:3, delta=+10)."""
    pytest.skip("TODO")


def test_regra_atraso_define_atraso_da_voz():
    pytest.skip("TODO")


def test_mapeamento_usa_regra_padrao_quando_nenhuma_aceita():
    pytest.skip("TODO")


def test_mapeamento_aceita_regra_nova_sem_mudar_codigo():
    """adicionar_regra com uma regra de teste para '@' — demonstra OCP."""
    pytest.skip("TODO")
