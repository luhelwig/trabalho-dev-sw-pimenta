"""Classe Player (Fase 1, adaptada na Fase 2).

Fase 3: play()/stop() viraram tocar()/parar(), os mesmos nomes do
BackendAudio e do ControladorAplicacao (antes eram dois vocabulários para
a mesma ação).
"""

from pathlib import Path
import tempfile
import mido
from gerador_musical.excecoes import MusicaNaoGeradaErro

from gerador_musical.saida.backend_audio import BackendAudio


class Player:
    """Controla a reprodução da música já gerada.

    Tocar de novo não reinterpreta o texto: reusa `musica`. A reprodução é
    assíncrona (o backend toca em segundo plano), então a interface continua
    respondendo (requisito não-funcional).

    Attributes:
        em_reproducao: True depois de tocar() e até parar().
        pausado: True enquanto estiver pausado.
        musica: último MIDI carregado (None se nada foi gerado).
    """

    def __init__(self, backend: BackendAudio) -> None:
        """Cria o player, sem música carregada.

        Args:
            backend: o "aparelho de som" (BackendPygame ou um falso nos testes).
        """
        self.em_reproducao: bool = False
        self.pausado: bool = False
        self.musica: mido.MidiFile | None = None
        self._backend: BackendAudio = backend
        self._arquivo_temporario: Path | None = None

    def carregar(self, musica: mido.MidiFile) -> None:
        """NOVO — guarda a música e grava o MIDI num arquivo temporário.

        O pygame toca a partir de arquivo, por isso a música é salva em
        "gerador_musical.mid" na pasta temporária do sistema. Antes, para o que
        estiver tocando.

        Args:
            musica: MIDI gerado pelo Sintetizador.
        """
        self.parar()  # solta o arquivo anterior, se houver
        self.musica = musica
        self._arquivo_temporario = Path(tempfile.gettempdir()) / "gerador_musical.mid"
        musica.save(str(self._arquivo_temporario))

    def tocar(self) -> None:
        """Toca a música do início.

        Raises:
            MusicaNaoGeradaErro: nada foi carregado.
            AudioIndisponivelErro: este computador não consegue tocar MIDI.
        """
        if self.musica is None:
            raise MusicaNaoGeradaErro("Gere a música antes de tocar.")
        self._backend.carregar(self._arquivo_temporario)
        self._backend.tocar()
        self.em_reproducao = True
        self.pausado = False

    def parar(self) -> None:
        """Para a reprodução e zera os estados."""
        self._backend.parar()
        self.em_reproducao = False
        self.pausado = False

    def pausar(self) -> None:
        """Pausa, se estiver tocando e ainda não estiver pausado."""
        if self.em_reproducao and not self.pausado:
            self._backend.pausar()
            self.pausado = True

    def retomar(self) -> None:
        """Retoma, se estiver tocando e estiver pausado."""
        if self.em_reproducao and self.pausado:
            self._backend.retomar()
            self.pausado = False

    def terminou(self) -> bool:
        """NOVO — diz se a música acabou sozinha.

        Usado para a mensagem de conclusão: a interface consulta isto
        periodicamente (tk.after). Pausado não conta como terminado, porque o
        pygame também responde "não estou tocando" durante a pausa.

        Returns:
            True se estava tocando, não está pausado e o backend parou.
        """
        return self.em_reproducao and not self.pausado and not self._backend.esta_tocando()
