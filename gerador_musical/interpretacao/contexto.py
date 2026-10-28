"""NOVA (Fase 2): estado compartilhado entre as regras enquanto UMA linha é lida."""

from gerador_musical.interpretacao.tokens import Token
from gerador_musical.musica.evento_musical import EventoMusical
from gerador_musical.musica.parametros_musica import ParametrosMusica
from gerador_musical.musica.partitura import Partitura
from gerador_musical.musica.voz import Voz


class ContextoInterpretacao:
    """O que uma regra pode ler e alterar ao ser aplicada.

    `nota_anterior` ficava no Parser na Fase 1. Veio para cá porque são as
    regras que precisam dela, e elas não devem depender do Parser (DIP). Um
    contexto novo é criado para cada linha, então essa memória não passa de
    uma voz para outra.

    Attributes:
        voz: voz que está sendo montada.
        partitura: partitura da música inteira (para mudanças de andamento).
        token_anterior: último token processado nesta linha.
        nota_anterior: último evento do tipo nota desta linha.
    """

    def __init__(self, voz: Voz, partitura: Partitura) -> None:
        """Cria o contexto de uma linha, sem token nem nota anteriores.

        Args:
            voz: voz que está sendo montada.
            partitura: partitura da música.
        """
        self.voz: Voz = voz
        self.partitura: Partitura = partitura
        self.token_anterior: Token | None = None
        self.nota_anterior: EventoMusical | None = None

    def parametros(self) -> ParametrosMusica:
        """Atalho para os parâmetros da voz atual."""
        return self.voz.parametros

    def registrar_evento(self, evento: EventoMusical) -> None:
        """Adiciona o evento na voz e, se for nota, guarda como nota_anterior.

        Args:
            evento: nota ou pausa criada por uma regra.
        """
        self.voz.adicionar_evento(evento)
        if evento.eh_nota():
            self.nota_anterior = evento

    def anterior_foi_nota(self) -> bool:
        """Diz se o token processado imediatamente antes era uma nota.

        Usado pela regra padrão: depois de uma nota, um caractere sem regra
        própria repete a nota; depois de qualquer outra coisa, vira pausa.
        """
        return self.token_anterior is not None and self.token_anterior.eh_nota()

    def avancar(self, token: Token) -> None:
        """Marca o token como "anterior" (chamado pelo Parser após cada regra).

        Args:
            token: token que acabou de ser aplicado.
        """
        self.token_anterior = token

    def posicao_atual_beats(self) -> float:
        """Devolve a posição atual da voz, em beats."""
        return self.voz.posicao_atual_beats()
