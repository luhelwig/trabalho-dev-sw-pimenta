"""Classe EventoMusical (Fase 1, adaptada na Fase 2)."""

from dataclasses import dataclass
from enum import Enum, auto

from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.nota_musical import NotaMusical
from gerador_musical.musica.parametros_musica import ParametrosMusica


class TipoEvento(Enum):
    """Tipo de evento: NOTA (soa) ou PAUSA (silêncio)."""

    NOTA = auto()
    PAUSA = auto()


@dataclass
class EventoMusical:
    """Algo que ocupa tempo na linha do tempo de uma voz: nota ou pausa.

    Cada nota guarda uma "foto" dos parâmetros da voz no momento em que foi
    lida (instrumento, oitava, volume). Assim o Sintetizador não precisa
    reinterpretar comandos, e um comando lido depois não altera notas que
    já foram criadas.

    Mudanças em relação à Fase 1: `nota` virou NotaMusical (letra +
    acidente); `duracao` virou o enum Duracao; eh_acao() saiu, porque
    comandos não viram eventos (só alteram ParametrosMusica ou registram
    MudancaAndamento na Partitura).

    Attributes:
        tipo: NOTA ou PAUSA.
        duracao: figura de duração.
        nota: a nota (None em pausas).
        instrumento: programa MIDI da nota (None em pausas).
        oitava: oitava da nota (None em pausas).
        volume: volume da nota, 0–127 (None em pausas).
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
        """Cria uma nota copiando instrumento, oitava e volume ATUAIS da voz.

        Args:
            nota: letra + acidente.
            duracao: figura de duração.
            parametros: parâmetros atuais da voz.

        Returns:
            Evento do tipo NOTA.
        """
        return cls(
            tipo=TipoEvento.NOTA,
            duracao=duracao,
            nota=nota,
            instrumento=parametros.get_instrumento(),
            oitava=parametros.get_oitava(),
            volume=parametros.get_volume())

    @classmethod
    def criar_pausa(cls, duracao: Duracao) -> "EventoMusical":
        """Cria uma pausa (silêncio) com a duração dada.

        Args:
            duracao: figura de duração.

        Returns:
            Evento do tipo PAUSA.
        """
        return cls(
            tipo=TipoEvento.PAUSA,
            duracao=duracao
        )

    def eh_nota(self) -> bool:
        """Diz se o evento é uma nota."""
        return self.tipo is TipoEvento.NOTA

    def eh_pausa(self) -> bool:
        """Diz se o evento é uma pausa."""
        return self.tipo is TipoEvento.PAUSA

    def altura_midi(self) -> int:
        """NOVO — número MIDI da nota (nota.altura_midi(oitava)).

        Returns:
            Altura MIDI de 0 a 127.

        Raises:
            ValueError: se o evento for pausa.
        """
        if self.nota is None:
            raise ValueError("Pausa sem altura")
        else:
            return self.nota.altura_midi(self.oitava)

    def duracao_em_beats(self) -> float:
        """Devolve a duração do evento em beats."""
        return self.duracao.em_beats()
