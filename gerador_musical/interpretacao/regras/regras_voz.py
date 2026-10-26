"""Regras que alteram apenas a voz atual (atraso, volume, oitava, instrumento)."""

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.regras.regra_mapeamento import (
    RegraMapeamento,
    RegraPorCaractere,
)
from gerador_musical.interpretacao.tokens import TipoToken, Token
from gerador_musical.musica.limites import PROGRAMA_MIDI_MAXIMO


class RegraAtraso(RegraMapeamento):
    """Token ATRASO "[n]" -> a voz começa após n beats de silêncio."""

    def aceita(self, token: Token) -> bool:
        """Aceita tokens do tipo ATRASO."""
        return token.tipo is TipoToken.ATRASO

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Define o atraso da voz com o valor do token.

        Args:
            token: token ATRASO.
            contexto: estado da linha.
        """
        contexto.voz.set_atraso(token.valor)


class RegraVolume(RegraPorCaractere):
    """Espaço -> dobra o volume da voz (máximo 127).

    Decisão do grupo: mantivemos o espaço como no enunciado. Em textos com
    espaços entre as notas, o volume chega rápido ao máximo; para trocar o
    caractere, basta mudar o argumento em Mapeamento.padrao().
    """

    def __init__(self, caracteres: str = " ") -> None:
        """Cria a regra.

        Args:
            caracteres: caracteres que dobram o volume (padrão: espaço).
        """
        super().__init__(caracteres)

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Dobra o volume atual da voz.

        Args:
            token: token CARACTERE.
            contexto: estado da linha.
        """
        contexto.parametros().dobrar_volume()


class RegraOitava(RegraPorCaractere):
    """Sobe ('?') ou desce ('V') uma oitava.

    Uma classe só, parametrizada pelo sentido (+1/-1), em vez de duas
    classes quase iguais.

    Attributes:
        sentido: +1 para subir, -1 para descer.
    """

    def __init__(self, caracteres: str, sentido: int) -> None:
        """Cria a regra.

        Args:
            caracteres: caracteres que disparam a regra (ex.: "?").
            sentido: +1 para subir, -1 para descer.
        """
        super().__init__(caracteres)
        self.sentido: int = sentido

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Sobe ou desce a oitava atual da voz, conforme o sentido.

        Args:
            token: token CARACTERE.
            contexto: estado da linha.
        """
        if self.sentido > 0:
            contexto.parametros().incrementar_oitava()
        else:
            contexto.parametros().decrementar_oitava()

class RegraInstrumentoFixo(RegraPorCaractere):
    """Troca para um instrumento específico.

    Uma classe reaproveitada em três linhas da tabela: '!' -> Bandoneon;
    ';' e dígitos ímpares -> Sinos tubulares; ',' -> Agogô.

    Attributes:
        programa: programa MIDI do instrumento.
    """

    def __init__(self, caracteres: str, programa: int) -> None:
        """Cria a regra.

        Args:
            caracteres: caracteres que disparam a troca.
            programa: programa MIDI do instrumento.
        """
        super().__init__(caracteres)
        self.programa: int = programa

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Troca o instrumento atual da voz pelo programa da regra.

        Args:
            token: token CARACTERE.
            contexto: estado da linha.
        """
        contexto.parametros().set_instrumento(self.programa)


class RegraInstrumentoSomaDigito(RegraPorCaractere):
    """Dígito par -> instrumento atual + valor do dígito.

    Só chegam aqui dígitos "soltos": os de ":n" e "[n]" já foram
    consumidos pelo Tokenizador. Se a soma passar de 127, recomeça do 0.
    """

    def __init__(self, caracteres: str = "02468") -> None:
        """Cria a regra.

        Args:
            caracteres: dígitos aceitos (padrão "02468").
        """
        super().__init__(caracteres)

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Soma o dígito ao instrumento atual, com módulo 128.

        Args:
            token: token CARACTERE com o dígito.
            contexto: estado da linha.
        """
        p= contexto.parametros()
        novo = (p.get_instrumento() + int(token.lexema))% (PROGRAMA_MIDI_MAXIMO + 1)
        p.set_instrumento(novo)
