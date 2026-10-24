import pytest

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.musica.parametros_musica import ParametrosMusica
from gerador_musical.musica.partitura import Partitura
from gerador_musical.musica.voz import Voz


@pytest.fixture
def contexto():
    voz = Voz(0, ParametrosMusica(instrumento_inicial=6, oitava_padrao=6, volume_padrao=40))
    return ContextoInterpretacao(voz, Partitura(bpm_inicial=120))