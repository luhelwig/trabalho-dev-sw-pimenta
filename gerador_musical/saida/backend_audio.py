"""NOVA (Fase 2): abstração do "aparelho de som".

O Player depende desta interface, não do pygame (DIP). Nos testes,
passa-se um backend falso que só registra as chamadas.
"""

from abc import ABC, abstractmethod
from pathlib import Path


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
        raise NotImplementedError

    def carregar(self, arquivo_midi: Path) -> None:
        raise NotImplementedError

    def tocar(self) -> None:
        raise NotImplementedError

    def pausar(self) -> None:
        raise NotImplementedError

    def retomar(self) -> None:
        raise NotImplementedError

    def parar(self) -> None:
        raise NotImplementedError

    def esta_tocando(self) -> bool:
        raise NotImplementedError
