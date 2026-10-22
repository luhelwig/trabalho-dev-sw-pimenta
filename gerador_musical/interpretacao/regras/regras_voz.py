"""Regras que alteram apenas a voz atual (atraso, volume, oitava, instrumento)."""

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.regras.regra_mapeamento import (
    RegraMapeamento,
    RegraPorCaractere,
)
from gerador_musical.interpretacao.tokens import Token


class RegraAtraso(RegraMapeamento):
    """Token ATRASO "[n]" -> a voz começa após n beats de silêncio."""

    def aceita(self, token: Token) -> bool:
        raise NotImplementedError

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError


class RegraVolume(RegraPorCaractere):
    """Espaço -> dobra o volume da voz (máximo 127).

    ATENÇÃO (decisão do grupo): o exemplo do enunciado "[4] C:2 D:2 E:3"
    usa espaço como separador. Com esta regra, o volume satura em 127 já
    no primeiro ou segundo espaço. Avaliem trocar o caractere aqui (só
    muda o argumento em Mapeamento.padrao()).
    """

    def __init__(self, caracteres: str = " ") -> None:
        super().__init__(caracteres)

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError


class RegraOitava(RegraPorCaractere):
    """Sobe ('?') ou desce ('V') uma oitava, relativa à oitava base da voz.

    Uma classe só, parametrizada pelo sentido (+1/-1), em vez de duas
    classes quase iguais.
    """

    def __init__(self, caracteres: str, sentido: int) -> None:
        super().__init__(caracteres)
        self.sentido: int = sentido

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError


class RegraInstrumentoFixo(RegraPorCaractere):
    """Troca para um instrumento específico.

    Ex.: '!' -> Bandoneon; ';' e dígitos ímpares -> Tubular Bells;
    ',' -> Agogô. Uma instância por linha da tabela.
    """

    def __init__(self, caracteres: str, programa: int) -> None:
        super().__init__(caracteres)
        self.programa: int = programa

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError


class RegraInstrumentoSomaDigito(RegraPorCaractere):
    """Dígito par -> instrumento atual + valor do dígito.

    Só chega aqui dígito "solto": os de ":n" e "[n]" são consumidos pelo
    Tokenizador.
    """

    def __init__(self, caracteres: str = "02468") -> None:
        super().__init__(caracteres)

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError
