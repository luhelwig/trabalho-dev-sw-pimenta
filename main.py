"""Ponto de entrada: monta as dependências e abre a interface.

Este é o único lugar que conhece as classes concretas de tudo
("composition root"). O resto do código recebe as dependências prontas.
"""

from gerador_musical.aplicacao.controlador import ControladorAplicacao
from gerador_musical.interface.app import App


def criar_controlador() -> ControladorAplicacao:
    """Instancia e conecta: CatalogoInstrumentos.padrao(),
    ConfiguracaoInicial.padrao(), Tokenizador, Mapeamento.padrao(catalogo),
    Parser, EntradaUsuario, Sintetizador, Player(BackendPygame()),
    ExportadorMidi -> ControladorAplicacao."""
    raise NotImplementedError


def main() -> None:
    app = App(criar_controlador())
    app.construir()
    app.mainloop()


if __name__ == "__main__":
    main()