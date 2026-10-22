"""NOVA (Fase 2): estado compartilhado entre as regras enquanto UMA linha é lida."""

from gerador_musical.interpretacao.tokens import Token
from gerador_musical.musica.evento_musical import EventoMusical
from gerador_musical.musica.parametros_musica import ParametrosMusica
from gerador_musical.musica.partitura import Partitura
from gerador_musical.musica.voz import Voz


class ContextoInterpretacao:
    """O que uma regra pode ler/alterar ao ser aplicada.

    `nota_anterior` estava no Parser na Fase 1. Veio para cá porque as
    regras precisam dela e não devem depender do Parser (DIP). Um
    contexto novo é criado para cada linha, então ela "zera" por voz.
    """

    def __init__(self, voz: Voz, partitura: Partitura) -> None:
        self.voz: Voz = voz
        self.partitura: Partitura = partitura
        self.token_anterior: Token | None = None
        self.nota_anterior: EventoMusical | None = None

    def parametros(self) -> ParametrosMusica:
        """Atalho para os parâmetros da voz atual."""
        raise NotImplementedError

    def registrar_evento(self, evento: EventoMusical) -> None:
        """Adiciona o evento na voz e, se for nota, atualiza nota_anterior."""
        raise NotImplementedError

    def anterior_foi_nota(self) -> bool:
        """True se o token processado imediatamente antes era uma nota.

        TODO (decisão do grupo): espaço entre notas ("C:3 H") conta como
        "anterior"? Se sim, H vira pausa; se não, repete C.
        """
        raise NotImplementedError

    def avancar(self, token: Token) -> None:
        """Chamado pelo Parser depois de cada regra: token atual vira anterior."""
        raise NotImplementedError

    def posicao_atual_beats(self) -> float:
        raise NotImplementedError
