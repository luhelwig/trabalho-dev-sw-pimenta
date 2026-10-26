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
    @abstractmethod
    def carregar(self, arquivo_midi: Path) -> None: ...

    @abstractmethod
    def tocar(self) -> None: ...

    @abstractmethod
    def pausar(self) -> None: ...

    @abstractmethod
    def retomar(self) -> None: ...

    @abstractmethod
    def parar(self) -> None: ...

    @abstractmethod
    def esta_tocando(self) -> bool: ...


class BackendPygame(BackendAudio):
    """Implementação com pygame.mixer.music (toca .mid direto).

    Usamos o pygame-ce (versão mantida pela comunidade, mesmo `import pygame`),
    que tem pacotes prontos para Python 3.14.

    No Windows e no macOS o MIDI sai pelo sintetizador do sistema. No Linux
    quem toca é o FluidSynth (que vem junto com o pygame-ce), e ele precisa
    de um banco de sons .sf2: procuramos um nos lugares de costume.
    """

    BANCOS_DE_SOM_LINUX = (
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",    # Ubuntu/Debian: fluid-soundfont-gm
        "/usr/share/soundfonts/FluidR3_GM.sf2",    # Fedora/Arch
        "/usr/share/sounds/sf2/default-GM.sf2",
        "/usr/share/soundfonts/default.sf2",
        "/usr/share/sounds/sf2/TimGM6mb.sf2",      # Ubuntu/Debian: timgm6mb-soundfont
    )

    def __init__(self) -> None:
        self._inicializado: bool = False

    def _garantir_inicializado(self) -> None:
        """pygame.mixer.init() uma única vez.

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
        """Linux: aponta SDL_SOUNDFONTS para o primeiro .sf2 encontrado,
        se o usuário ainda não tiver escolhido um."""
        if not sys.platform.startswith("linux") or "SDL_SOUNDFONTS" in os.environ:
            return
        for caminho in self.BANCOS_DE_SOM_LINUX:
            if Path(caminho).exists():
                os.environ["SDL_SOUNDFONTS"] = caminho
                return

    def carregar(self, arquivo_midi: Path) -> None:
        """Raises: AudioIndisponivelErro se este computador não toca MIDI."""
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
        pygame.mixer.music.play()

    def pausar(self) -> None:
        pygame.mixer.music.pause()

    def retomar(self) -> None:
        pygame.mixer.music.unpause()

    def parar(self) -> None:
        if not self._inicializado:
            return
        else:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

    def esta_tocando(self) -> bool:
        if not self._inicializado:
            return False
        else:
            return pygame.mixer.music.get_busy()
