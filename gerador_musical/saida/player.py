"""Classe Player (Fase 1, adaptada na Fase 2)."""

from pathlib import Path
import tempfile
import mido
from gerador_musical.excecoes import MusicaNaoGeradaErro

from gerador_musical.saida.backend_audio import BackendAudio


class Player:
    """Controla a reprodução da música já gerada.

    Tocar de novo não reinterpreta o texto: reusa `musica`.
    A reprodução é assíncrona (o backend toca em segundo plano), então a
    interface continua respondendo (requisito não-funcional).
    """

    def __init__(self, backend: BackendAudio) -> None:
        self.em_reproducao: bool = False
        self.pausado: bool = False
        self.musica: mido.MidiFile | None = None
        self._backend: BackendAudio = backend
        self._arquivo_temporario: Path | None = None

    def carregar(self, musica: mido.MidiFile) -> None:
        """NOVO — guarda a música e a entrega ao backend.

        pygame toca a partir de arquivo: salvar `musica` num arquivo
        temporário (tempfile) e passar o caminho ao backend.
        """
        self.stop()  # solta o arquivo anterior, se houver
        self.musica = musica
        self._arquivo_temporario = Path(tempfile.gettempdir()) / "gerador_musical.mid"
        musica.save(str(self._arquivo_temporario))

    def play(self) -> None:
        """Toca do início.

        Raises:
            MusicaNaoGeradaErro: nada carregado.
        """
        if self.musica is None:
            raise MusicaNaoGeradaErro("Gere a música antes de tocar.")
        self._backend.carregar(self._arquivo_temporario)
        self._backend.tocar()
        self.em_reproducao = True
        self.pausado = False

    def stop(self) -> None:
        self._backend.parar()
        self.em_reproducao = False
        self.pausado = False

    def pausar(self) -> None:
        if self.em_reproducao and not self.pausado:
            self._backend.pausar()
            self.pausado = True


    def retomar(self) -> None:
        if self.em_reproducao and self.pausado:
            self._backend.retomar()
            self.pausado = False

    def terminou(self) -> bool:
        """NOVO — True quando a música acabou sozinha (para a mensagem de
        conclusão). A interface consulta isto periodicamente (tk.after)."""
        return self.em_reproducao and not self.pausado and not self._backend.esta_tocando()
