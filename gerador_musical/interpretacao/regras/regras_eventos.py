"""Regras que geram eventos (nota/pausa) na voz."""

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.regras.regra_mapeamento import (
    RegraMapeamento,
    RegraPorCaractere,
)
from gerador_musical.interpretacao.tokens import Token


class RegraNota(RegraMapeamento):
    """Token NOTA ("A", "C#:3", "Eb:2") -> evento de nota.

    Usa a duração do token ou Duracao.padrao() se não houver ":n".
    """

    def aceita(self, token: Token) -> bool:
        raise NotImplementedError

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError


class RegraPausa(RegraPorCaractere):
    """Letras minúsculas a–h -> pausa (silêncio).

    'b' só chega aqui quando NÃO está logo após uma nota (senão o
    Tokenizador já o consumiu como bemol).
    """

    def __init__(self, caracteres: str = "abcdefgh") -> None:
        super().__init__(caracteres)

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError


class RegraRepetirOuPausar(RegraMapeamento):
    """Regra padrão (ELSE): aceita qualquer token.

    Se o token anterior era nota, repete a última nota; senão, pausa.
    Cobre H, consoantes não classificadas e — pela Fase 2 — as vogais
    O, I, U.

    TODO (decisão do grupo): a nota repetida usa a duração da original?
    E os parâmetros atuais da voz ou os da nota original?
    """

    def aceita(self, token: Token) -> bool:
        raise NotImplementedError

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError
