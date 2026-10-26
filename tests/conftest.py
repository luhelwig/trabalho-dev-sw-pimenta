"""Fixtures compartilhadas pelos testes (o pytest lê este arquivo sozinho)."""
import pytest

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.musica.parametros_musica import ParametrosMusica
from gerador_musical.musica.partitura import Partitura
from gerador_musical.musica.voz import Voz
from gerador_musical.saida.backend_audio import BackendAudio

@pytest.fixture
def contexto():
    """Contexto de interpretação novo para cada teste.

    Uma voz com instrumento 6 (Cravo), oitava 6 e volume 40, numa partitura
    vazia com BPM 120.
    """
    voz = Voz(0, ParametrosMusica(instrumento_inicial=6, oitava_padrao=6, volume_padrao=40))
    return ContextoInterpretacao(voz, Partitura(bpm_inicial=120))

class BackendFalso(BackendAudio):
    """Finge ser o pygame: só anota o que foi chamado, sem tocar nada.

    Attributes:
        chamadas: nomes dos métodos chamados, em ordem.
        tocando: o que esta_tocando() responde.
    """

    def __init__(self):
        """Começa sem chamadas e sem tocar."""
        self.chamadas = []
        self.tocando = False

    def carregar(self, arquivo_midi):
        """Anota "carregar"."""
        self.chamadas.append("carregar")

    def tocar(self):
        """Anota "tocar" e passa a responder que está tocando."""
        self.chamadas.append("tocar")
        self.tocando = True

    def pausar(self):
        """Anota "pausar"."""
        self.chamadas.append("pausar")

    def retomar(self):
        """Anota "retomar"."""
        self.chamadas.append("retomar")

    def parar(self):
        """Anota "parar" e passa a responder que não está tocando."""
        self.chamadas.append("parar")
        self.tocando = False

    def esta_tocando(self):
        """Devolve o valor de self.tocando."""
        return self.tocando


@pytest.fixture
def backend():
    """Backend falso novo para cada teste do Player."""
    return BackendFalso()