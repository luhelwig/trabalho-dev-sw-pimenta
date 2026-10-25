"""Ponto de entrada: monta as dependências e abre a interface.

Este é o único lugar que conhece as classes concretas de tudo
("composition root"). O resto do código recebe as dependências prontas.
"""

from gerador_musical.aplicacao.controlador import ControladorAplicacao
from gerador_musical.entrada.entrada_usuario import EntradaUsuario
from gerador_musical.interface.app import App
from gerador_musical.interpretacao.parser import Parser
from gerador_musical.interpretacao.regras.mapeamento import Mapeamento
from gerador_musical.interpretacao.tokenizador import Tokenizador
from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial
from gerador_musical.musica.instrumentos import CatalogoInstrumentos
from gerador_musical.saida.backend_audio import BackendPygame
from gerador_musical.saida.exportador import ExportadorMidi
from gerador_musical.saida.player import Player
from gerador_musical.saida.sintetizador import Sintetizador


def criar_controlador() -> ControladorAplicacao:
    """Instancia e conecta: CatalogoInstrumentos.padrao(),
    ConfiguracaoInicial.padrao(), Tokenizador, Mapeamento.padrao(catalogo),
    Parser, EntradaUsuario, Sintetizador, Player(BackendPygame()),
    ExportadorMidi -> ControladorAplicacao."""
    catalogo = CatalogoInstrumentos.padrao()
    configuracao = ConfiguracaoInicial.padrao()
    parser = Parser(Tokenizador(), Mapeamento.padrao(), configuracao)
    return ControladorAplicacao(
        entrada=EntradaUsuario(), parser=parser, configuracao=configuracao,
        sintetizador=Sintetizador(), player=Player(BackendPygame()),
        exportador=ExportadorMidi(), catalogo=catalogo,
    )


def main() -> None:
    app = App(criar_controlador())
    app.construir()
    app.mainloop()


if __name__ == "__main__":
    main()