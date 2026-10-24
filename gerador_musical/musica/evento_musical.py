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
        return cls(
            tipo=TipoEvento.NOTA,
            duracao=duracao,
            nota=nota,
            instrumento=parametros.get_instrumento(),
            oitava=parametros.get_oitava(),
            volume=parametros.get_volume())

    @classmethod
    def criar_pausa(cls, duracao: Duracao) -> "EventoMusical":
        return cls(
            tipo=TipoEvento.PAUSA,
            duracao=duracao
        )

    def eh_nota(self) -> bool:
        return self.tipo is TipoEvento.NOTA

    def eh_pausa(self) -> bool:
        return self.tipo is TipoEvento.PAUSA

    def altura_midi(self) -> int:
        """NOVO — número MIDI da nota (usa nota.altura_midi(oitava)).

        Raises:
            ValueError: se o evento for pausa.
        """
        if self.nota is None:
            raise ValueError("Pausa sem altura")
        else:
            return self.nota.altura_midi(self.oitava)

    def duracao_em_beats(self) -> float:
        return self.duracao.em_beats()
