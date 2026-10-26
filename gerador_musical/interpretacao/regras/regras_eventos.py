"""Regras que geram eventos (nota ou pausa) na voz."""

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.regras.regra_mapeamento import (
    RegraMapeamento,
    RegraPorCaractere,
)
from gerador_musical.interpretacao.tokens import Token
from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.evento_musical import EventoMusical

class RegraNota(RegraMapeamento):
    """Token NOTA ("A", "C#:3", "Eb:2") -> evento de nota."""

    def aceita(self, token: Token) -> bool:
        """Aceita tokens do tipo NOTA."""
        return token.eh_nota()

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Cria a nota com os parâmetros atuais da voz e registra no contexto.

        Usa a duração do token ou, se não houver ":n", Duracao.padrao().

        Args:
            token: token NOTA.
            contexto: estado da linha.
        """
        duracao = token.duracao or Duracao.padrao()
        contexto.registrar_evento(EventoMusical.criar_nota(token.nota, duracao, contexto.parametros()))


class RegraPausa(RegraPorCaractere):
    """Letras minúsculas a–h -> pausa (silêncio).

    Um 'b' logo depois de uma nota nunca chega aqui: o Tokenizador já o
    leu como bemol.
    """

    def __init__(self, caracteres: str = "abcdefgh") -> None:
        """Cria a regra com os caracteres de pausa.

        Args:
            caracteres: caracteres que viram pausa (padrão "abcdefgh").
        """
        super().__init__(caracteres)

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Registra uma pausa de duração padrão.

        Args:
            token: token CARACTERE de pausa.
            contexto: estado da linha.
        """
        contexto.registrar_evento(EventoMusical.criar_pausa(Duracao.padrao()))


class RegraRepetirOuPausar(RegraMapeamento):
    """Regra padrão (o "senão" da tabela): aceita qualquer token.

    Se o token anterior era nota, repete essa nota; senão, faz uma pausa.
    Cobre H, O, I, U, as outras letras sem regra própria e os símbolos.

    Decisão do grupo: a nota repetida mantém a letra e a duração da
    original, com os parâmetros atuais da voz.
    """

    def aceita(self, token: Token) -> bool:
        """Aceita qualquer token (é a regra usada quando nenhuma outra aceita)."""
        return True

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Repete a nota anterior ou registra uma pausa.

        Args:
            token: token sem regra própria.
            contexto: estado da linha (diz se o anterior foi nota).
        """
        if contexto.anterior_foi_nota() and contexto.nota_anterior is not None:
            evento = EventoMusical.criar_nota(
                contexto.nota_anterior.nota, contexto.nota_anterior.duracao, contexto.parametros()
            )
        else:
            evento = EventoMusical.criar_pausa(Duracao.padrao())
        contexto.registrar_evento(evento)

