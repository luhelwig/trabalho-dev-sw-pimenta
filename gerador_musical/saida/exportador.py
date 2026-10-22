"""NOVA (Fase 2, Mudança 2): salvar a música gerada em arquivo."""

from abc import ABC, abstractmethod
from pathlib import Path

import mido


class Exportador(ABC):
    """Abstração para formatos de saída (MIDI hoje; WAV/MP3 no futuro)."""

    @abstractmethod
    def exportar(self, midi: mido.MidiFile, destino: Path | None = None) -> Path:
        """Grava o arquivo e devolve o caminho final."""


class ExportadorMidi(Exportador):
    """Grava .mid.

    Decisão (requisitos): diretório padrão = Downloads do usuário e nome
    padronizado. TODO: definir o padrão do nome (documentação diz "XXX").
    Sugestão: "musica_AAAAMMDD_HHMMSS.mid" (nunca sobrescreve).
    """

    EXTENSAO = ".mid"

    def __init__(self, diretorio: Path | None = None) -> None:
        self.diretorio: Path | None = diretorio  # None = diretorio_padrao()

    def exportar(self, midi: mido.MidiFile, destino: Path | None = None) -> Path:
        raise NotImplementedError

    def diretorio_padrao(self) -> Path:
        """~/Downloads (criar se não existir?)."""
        raise NotImplementedError

    def gerar_nome_padrao(self) -> str:
        raise NotImplementedError
