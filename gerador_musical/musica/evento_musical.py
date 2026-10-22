"""Classe EventoMusical (Fase 1, adaptada na Fase 2)."""

from dataclasses import dataclass
from enum import Enum, auto

from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.nota_musical import NotaMusical
from gerador_musical.musica.parametros_musica import ParametrosMusica


class TipoEvento(Enum):
    NOTA = auto()
    PAUSA = auto()


@dataclass
class EventoMusical:
    """Algo que ocupa tempo na linha do tempo de uma voz: nota ou pausa.

    Cada nota guarda uma "foto" dos parâmetros da voz no momento em que
    foi lida (instrumento, oitava, volume). Assim o Sintetizador não
    precisa reinterpretar comandos.

    MUDANÇAS EM RELAÇÃO À FASE 1:
      - `nota` virou NotaMusical (letra + acidente);
      - `duracao` virou o enum Duracao;
      - eh_acao() saiu: comandos (volume, oitava, instrumento) não viram
        eventos, só alteram ParametrosMusica; mudança de BPM vira
        MudancaAndamento na Partitura.
    """

    tipo: TipoEvento
    duracao: Duracao
    nota: NotaMusical | None = None
    instrumento: int | None = None
    oitava: int | None = None
    volume: int | None = None

    @classmethod
    def criar_nota(
        cls, nota: NotaMusical, duracao: Duracao, parametros: ParametrosMusica
    ) -> "EventoMusical":
        """Cria uma nota copiando instrumento/oitava/volume ATUAIS da voz."""
        raise NotImplementedError

    @classmethod
    def criar_pausa(cls, duracao: Duracao) -> "EventoMusical":
        raise NotImplementedError

    def eh_nota(self) -> bool:
        raise NotImplementedError

    def eh_pausa(self) -> bool:
        raise NotImplementedError

    def altura_midi(self) -> int:
        """NOVO — número MIDI da nota (usa nota.altura_midi(oitava)).

        Raises:
            ValueError: se o evento for pausa.
        """
        raise NotImplementedError

    def duracao_em_beats(self) -> float:
        raise NotImplementedError
