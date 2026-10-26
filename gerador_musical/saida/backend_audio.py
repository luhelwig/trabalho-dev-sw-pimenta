"""NOVA (Fase 2): abstração do "aparelho de som".

O Player depende desta interface, não do pygame (DIP). Nos testes,
passa-se um backend falso que só registra as chamadas.
"""

import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path

import pygame

from gerador_musical.excecoes import AudioIndisponivelErro


class BackendAudio(ABC):
    """Interface do que o Player precisa para tocar um arquivo MIDI."""

    @abstractmethod
    def carregar(self, arquivo_midi: Path) -> None:
        """Prepara o arquivo MIDI para tocar.

        Args:
            arquivo_midi: caminho do arquivo .mid.
        """

    @abstractmethod
    def tocar(self) -> None:
        """Começa a tocar do início."""

    @abstractmethod
    def pausar(self) -> None:
        """Pausa a reprodução, guardando a posição."""

    @abstractmethod
    def retomar(self) -> None:
        """Continua a reprodução de onde pausou."""

    @abstractmethod
    def parar(self) -> None:
        """Para a reprodução e libera o arquivo."""

    @abstractmethod
    def esta_tocando(self) -> bool:
        """Diz se há música tocando agora."""


class BackendPygame(BackendAudio):
    """Implementação com pygame.mixer.music (toca .mid direto).

    Usamos o pygame-ce (versão mantida pela comunidade, mesmo `import pygame`),
    que tem pacotes prontos para Python 3.14.

    No Windows e no macOS o MIDI sai pelo sintetizador do sistema. No Linux
    quem toca é o FluidSynth (que vem junto com o pygame-ce), e ele precisa
    de um banco de sons .sf2: procuramos um nos lugares de costume.

    Attributes:
        BANCOS_DE_SOM_LINUX: onde as distribuições Linux costumam instalar
            bancos de sons General MIDI.
    """

    BANCOS_DE_SOM_LINUX = (
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",    # Ubuntu/Debian: fluid-soundfont-gm
        "/usr/share/soundfonts/FluidR3_GM.sf2",    # Fedora/Arch
        "/usr/share/sounds/sf2/default-GM.sf2",
        "/usr/share/soundfonts/default.sf2",
        "/usr/share/sounds/sf2/TimGM6mb.sf2",      # Ubuntu/Debian: timgm6mb-soundfont
    )

    def __init__(self) -> None:
        """Cria o backend; o mixer do pygame só é iniciado no primeiro uso."""
        self._inicializado: bool = False

    def _garantir_inicializado(self) -> None:
        """Inicia o mixer do pygame uma única vez (inicialização preguiçosa).

        Raises:
            AudioIndisponivelErro: pygame instalado sem o módulo de som.
        """
        if not self._inicializado:
            self._escolher_banco_de_som()
            try:
                pygame.mixer.init()
            except (NotImplementedError, pygame.error) as erro:
                raise AudioIndisponivelErro(f"Não foi possível usar o som: {erro}") from erro
            self._inicializado = True

    def _escolher_banco_de_som(self) -> None:
        """Linux: aponta SDL_SOUNDFONTS para o primeiro .sf2 encontrado.

        Não faz nada fora do Linux ou se o usuário já escolheu um banco de sons
        na variável de ambiente.
        """
        if not sys.platform.startswith("linux") or "SDL_SOUNDFONTS" in os.environ:
            return
        for caminho in self.BANCOS_DE_SOM_LINUX:
            if Path(caminho).exists():
                os.environ["SDL_SOUNDFONTS"] = caminho
                return

    def carregar(self, arquivo_midi: Path) -> None:
        """Inicia o mixer, se preciso, e carrega o arquivo MIDI.

        Args:
            arquivo_midi: caminho do arquivo .mid.

        Raises:
            AudioIndisponivelErro: se este computador não consegue tocar MIDI
                (ex.: Linux sem banco de sons).
        """
        self._garantir_inicializado()
        try:
            pygame.mixer.music.load(str(arquivo_midi))
        except pygame.error as erro:
            raise AudioIndisponivelErro(
                "Este computador não conseguiu tocar MIDI. No Linux, instale um banco de "
                "sons (Ubuntu: sudo apt install fluid-soundfont-gm). O arquivo .mid pode "
                f"ser salvo normalmente.\n\nDetalhe: {erro}"
            ) from erro

    def tocar(self) -> None:
        """Começa a tocar do início (pygame.mixer.music.play)."""
        pygame.mixer.music.play()

    def pausar(self) -> None:
        """Pausa a reprodução (pygame.mixer.music.pause)."""
        pygame.mixer.music.pause()

    def retomar(self) -> None:
        """Continua de onde pausou (pygame.mixer.music.unpause)."""
        pygame.mixer.music.unpause()

    def parar(self) -> None:
        """Para e descarrega o arquivo, se o mixer já foi iniciado."""
        if not self._inicializado:
            return
        else:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

    def esta_tocando(self) -> bool:
        """Diz se o pygame está tocando (False se o mixer nem foi iniciado)."""
        if not self._inicializado:
            return False
        else:
            return pygame.mixer.music.get_busy()
