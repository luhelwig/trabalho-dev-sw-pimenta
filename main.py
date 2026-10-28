"""Ponto de entrada do Gerador de Música a partir de Texto.

Monta todas as dependências e abre a interface. Este é o único lugar que
conhece as classes concretas de tudo (a "composition root"); o resto do
código recebe as dependências prontas pelo construtor.

Para rodar: python main.py
"""

from gerador_musical.aplicacao.controlador import ControladorAplicacao
from gerador_musical.aplicacao.controlador_configuracao import ControladorConfiguracao
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


def criar_controladores() -> tuple[ControladorAplicacao, ControladorConfiguracao]:
    """Instancia e conecta todas as peças do sistema.

    Cria o catálogo de instrumentos, a configuração inicial, o Parser (com
    Tokenizador e Mapeamento.padrao()), a entrada do usuário, o
    Sintetizador, o Player (com BackendPygame) e o ExportadorMidi. A mesma
    ConfiguracaoInicial vai para o Parser e para o ControladorConfiguracao:
    assim, o que a tela muda no painel é visto pelo Parser.

    Returns:
        (ControladorAplicacao, ControladorConfiguracao), prontos para a interface.
    """
    catalogo = CatalogoInstrumentos.padrao()
    configuracao = ConfiguracaoInicial.padrao()
    parser = Parser(Tokenizador(), Mapeamento.padrao(), configuracao)
    controlador = ControladorAplicacao(
        entrada=EntradaUsuario(), parser=parser, sintetizador=Sintetizador(),
        player=Player(BackendPygame()), exportador=ExportadorMidi(),
    )
    return controlador, ControladorConfiguracao(configuracao, catalogo)


def main() -> None:
    """Cria a janela, monta as telas e entra no laço de eventos do tkinter."""
    app = App(*criar_controladores())
    app.construir()
    app.mainloop()


if __name__ == "__main__":
    main()
