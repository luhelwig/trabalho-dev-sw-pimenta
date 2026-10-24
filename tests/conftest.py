import pytest

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.musica.parametros_musica import ParametrosMusica
from gerador_musical.musica.partitura import Partitura
from gerador_musical.musica.voz import Voz
from gerador_musical.saida.backend_audio import BackendAudio

@pytest.fixture
def contexto():
    voz = Voz(0, ParametrosMusica(instrumento_inicial=6, oitava_padrao=6, volume_padrao=40))
    return ContextoInterpretacao(voz, Partitura(bpm_inicial=120))

class BackendFalso(BackendAudio):
    """Finge ser o pygame: só anota o que foi chamado, sem tocar nada."""

    def __init__(self):
        self.chamadas = []
        self.tocando = False

    def carregar(self, arquivo_midi):
        self.chamadas.append("carregar")

    def tocar(self):
        self.chamadas.append("tocar")
        self.tocando = True

    def pausar(self):
        self.chamadas.append("pausar")

    def retomar(self):
        self.chamadas.append("retomar")

    def parar(self):
        self.chamadas.append("parar")
        self.tocando = False

    def esta_tocando(self):
        return self.tocando


@pytest.fixture
def backend():
    return BackendFalso()