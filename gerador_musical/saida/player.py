"""Classe Player (Fase 1, adaptada na Fase 2).

Fase 3: play()/stop() viraram tocar()/parar(), os mesmos nomes do
BackendAudio e do ControladorAplicacao (antes eram dois vocabulários para
a mesma ação). O estado da reprodução, que eram dois booleanos
(em_reproducao e pausado), virou o Enum EstadoReproducao.
"""

from enum import Enum
from pathlib import Path
import tempfile
import mido
from gerador_musical.excecoes import MusicaNaoGeradaErro

from gerador_musical.saida.backend_audio import BackendAudio


class EstadoReproducao(Enum):
    """NOVO (Fase 3): em que ponto a reprodução está.

    Antes eram dois booleanos, em_reproducao e pausado: juntos eles
    representavam três estados e ainda permitiam um quarto, inválido
    (pausado sem estar tocando). E a TelaReproducao guardava uma cópia
    deles. Agora o estado existe num lugar só, aqui no Player, e a tela
    pergunta ao controlador (bad smell "Obsessão por Tipos Primitivos").
    """

    PARADA = "parada"
    TOCANDO = "tocando"
    PAUSADA = "pausada"


class Player:
    """Controla a reprodução da música já gerada.

    Tocar de novo não reinterpreta o texto: reusa `musica`. A reprodução é
    assíncrona (o backend toca em segundo plano), então a interface continua
    respondendo (requisito não-funcional).

    Attributes:
        estado: PARADA, TOCANDO ou PAUSADA.
        musica: último MIDI carregado (None se nada foi gerado).
    """

    def __init__(self, backend: BackendAudio) -> None:
        """Cria o player, sem música carregada.

        Args:
            backend: o "aparelho de som" (BackendPygame ou um falso nos testes).
        """
        self.estado: EstadoReproducao = EstadoReproducao.PARADA
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
        self.estado = EstadoReproducao.TOCANDO

    def parar(self) -> None:
        """Para a reprodução e volta ao estado PARADA."""
        self._backend.parar()
        self.estado = EstadoReproducao.PARADA

    def pausar(self) -> None:
        """Pausa, só se estiver TOCANDO."""
        if self.estado is EstadoReproducao.TOCANDO:
            self._backend.pausar()
            self.estado = EstadoReproducao.PAUSADA

    def retomar(self) -> None:
        """Retoma, só se estiver PAUSADA."""
        if self.estado is EstadoReproducao.PAUSADA:
            self._backend.retomar()
            self.estado = EstadoReproducao.TOCANDO

    def terminou(self) -> bool:
        """NOVO — diz se a música acabou sozinha.

        Usado para a mensagem de conclusão: a interface consulta isto
        periodicamente (tk.after). Pausado não conta como terminado, porque o
        pygame também responde "não estou tocando" durante a pausa.

        Returns:
            True se o estado é TOCANDO e o backend parou.
        """
        return self.estado is EstadoReproducao.TOCANDO and not self._backend.esta_tocando()
