"""NOVA (Fase 2, Mudança 3): catálogo de instrumentos General MIDI.

As constantes (PIANO, CRAVO, TUBULAR_BELLS...) são números de programa
MIDI de 0 a 127, que é o que o mido usa. Listas como a da Wikipédia
numeram de 1 a 128; o enunciado mistura as duas numerações, e aqui tudo
foi convertido para 0–127 (ex.: "Church Organ GM 20" = programa 19).
"""

from dataclasses import dataclass
PIANO = 0
CRAVO = 6
TUBULAR_BELLS = 14
ORGAO_DE_IGREJA = 19
BANDONEON = 23
CORDAS = 48
FAGOTE = 70
GAITA_DE_FOLES = 109
AGOGO = 113


@dataclass(frozen=True)
class Instrumento:
    """Instrumento General MIDI. Objeto de valor imutável.

    Attributes:
        programa: número de program change do MIDI (0–127).
        nome: nome exibido para o usuário.
    """

    programa: int
    nome: str


class CatalogoInstrumentos:
    """Instrumentos que o usuário pode escolher na interface (30, mínimo 25).

    Inclui todos os obrigatórios do enunciado: Piano, Cravo, Órgão de
    igreja, Sinos tubulares, Bandoneon, Cordas, Fagote, Gaita de foles,
    Agogô e Ondas do mar. As regras do texto podem gerar qualquer programa
    de 0 a 127, mesmo fora do catálogo.
    """

    def __init__(self, instrumentos: list[Instrumento]) -> None:
        """Guarda a lista e monta um índice programa -> Instrumento.

        Args:
            instrumentos: instrumentos na ordem em que devem aparecer na tela.
        """
        self._instrumentos: list[Instrumento] = instrumentos
        self._por_programa = {i.programa: i for i in instrumentos}

    @classmethod
    def padrao(cls) -> "CatalogoInstrumentos":
        """Cria o catálogo com os 30 instrumentos escolhidos pelo grupo.

        Returns:
            CatalogoInstrumentos com programas MIDI de 0 a 127.
        """
        """Catálogo com os 30 instrumentos escolhidos pelo grupo (programas MIDI 0–127)."""
        return cls([
            Instrumento(PIANO, "Piano"),
            Instrumento(CRAVO, "Cravo"),
            Instrumento(8, "Celesta"),
            Instrumento(9, "Glockenspiel"),
            Instrumento(10, "Caixinha de música"),
            Instrumento(11, "Vibrafone"),
            Instrumento(12, "Marimba"),
            Instrumento(13, "Xilofone"),
            Instrumento(TUBULAR_BELLS, "Sinos tubulares"),
            Instrumento(ORGAO_DE_IGREJA, "Órgão de igreja"),
            Instrumento(21, "Acordeão"),
            Instrumento(BANDONEON, "Bandoneon"),
            Instrumento(24, "Violão de nylon"),
            Instrumento(32, "Baixo acústico"),
            Instrumento(40, "Violino"),
            Instrumento(41, "Viola"),
            Instrumento(42, "Violoncelo"),
            Instrumento(46, "Harpa"),
            Instrumento(CORDAS, "Cordas"),
            Instrumento(52, "Coral"),
            Instrumento(56, "Trompete"),
            Instrumento(57, "Trombone"),
            Instrumento(60, "Trompa"),
            Instrumento(68, "Oboé"),
            Instrumento(FAGOTE, "Fagote"),
            Instrumento(71, "Clarinete"),
            Instrumento(73, "Flauta"),
            Instrumento(GAITA_DE_FOLES, "Gaita de foles"),
            Instrumento(AGOGO, "Agogô"),
            Instrumento(122, "Ondas do mar"),
        ])

    def listar(self) -> list[Instrumento]:
        """Devolve uma cópia da lista de instrumentos, na ordem de exibição."""
        return list(self._instrumentos)

    def buscar(self, programa: int) -> Instrumento:
        """Procura um instrumento pelo número do programa.

        Args:
            programa: número de programa MIDI.

        Returns:
            O Instrumento correspondente.

        Raises:
            KeyError: se o programa não estiver no catálogo.
        """
        return self._por_programa[programa]

    def contem(self, programa: int) -> bool:
        """Diz se o programa MIDI está no catálogo."""
        return programa in self._por_programa

    def nome_de(self, programa: int) -> str:
        """Devolve o nome do instrumento de um programa MIDI.

        Raises:
            KeyError: se o programa não estiver no catálogo.
        """
        return self.buscar(programa).nome
