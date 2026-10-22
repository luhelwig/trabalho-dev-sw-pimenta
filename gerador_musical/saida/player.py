"""Classe Player (Fase 1, adaptada na Fase 2)."""

from pathlib import Path

import mido

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
        raise NotImplementedError

    def play(self) -> None:
        """Toca do início.

        Raises:
            MusicaNaoGeradaErro: nada carregado.
        """
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    def pausar(self) -> None:
        raise NotImplementedError

    def retomar(self) -> None:
        raise NotImplementedError

    def terminou(self) -> bool:
        """NOVO — True quando a música acabou sozinha (para a mensagem de
        conclusão). A interface consulta isto periodicamente (tk.after)."""
        raise NotImplementedError
