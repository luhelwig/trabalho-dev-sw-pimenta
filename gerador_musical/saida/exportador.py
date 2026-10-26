"""NOVA (Fase 2, Mudança 2): salvar a música gerada em arquivo."""

from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime

import mido


class Exportador(ABC):
    """Abstração para formatos de saída (MIDI hoje; WAV/MP3 no futuro)."""

    @abstractmethod
    def exportar(self, midi: mido.MidiFile, destino: Path | None = None) -> Path:
        """Grava o arquivo e devolve o caminho final.

        Args:
            midi: música gerada pelo Sintetizador.
            destino: caminho do arquivo; None para usar o padrão.

        Returns:
            Caminho do arquivo gravado.
        """


class ExportadorMidi(Exportador):
    """Grava arquivos .mid.

    Decisão do grupo: sem destino, salva na pasta Downloads do usuário com o
    nome musica_AAAAMMDD_HHMMSS.mid (data e hora), que nunca sobrescreve
    outro arquivo.

    Attributes:
        EXTENSAO: extensão dos arquivos gerados (".mid").
        diretorio: pasta padrão; None para usar Downloads.
    """

    EXTENSAO = ".mid"

    def __init__(self, diretorio: Path | None = None) -> None:
        """Cria o exportador.

        Args:
            diretorio: pasta onde salvar quando não houver destino; None para
                usar Downloads (os testes passam uma pasta temporária).
        """
        self.diretorio: Path | None = diretorio  # None = diretorio_padrao()

    def exportar(self, midi: mido.MidiFile, destino: Path | None = None) -> Path:
        """Grava o MIDI e devolve o caminho.

        Cria a pasta de destino se ela não existir.

        Args:
            midi: música gerada pelo Sintetizador.
            destino: caminho do arquivo; None para pasta padrão + nome padrão.

        Returns:
            Caminho do arquivo gravado.
        """
        if destino is None:
            pasta = self.diretorio or self.diretorio_padrao()
            destino = pasta / self.gerar_nome_padrao()
        destino.parent.mkdir(parents=True, exist_ok=True)
        midi.save(str(destino))
        return destino

    def diretorio_padrao(self) -> Path:
        """Devolve a pasta Downloads do usuário (~/Downloads)."""
        return Path.home() / "Downloads"

    def gerar_nome_padrao(self) -> str:
        """Devolve o nome padrão: musica_AAAAMMDD_HHMMSS.mid, com a hora atual."""
        return datetime.now().strftime("musica_%Y%m%d_%H%M%S") + self.EXTENSAO
