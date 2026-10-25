"""NOVA (Fase 2): abstração do "aparelho de som".

O Player depende desta interface, não do pygame (DIP). Nos testes,
passa-se um backend falso que só registra as chamadas.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import pygame


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

    Observação: no Windows/macOS funciona de imediato; no Linux o pygame
    precisa de um sintetizador MIDI configurado (ex.: timidity/fluidsynth).
    """

    def __init__(self) -> None:
        self._inicializado: bool = False

    def _garantir_inicializado(self) -> None:
        """pygame.mixer.init() uma única vez."""
        if not self._inicializado:
            pygame.mixer.init()
            self._inicializado = True

    def carregar(self, arquivo_midi: Path) -> None:
        self._garantir_inicializado()
        pygame.mixer.music.load(str(arquivo_midi))

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
