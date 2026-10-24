"""NOVA (Fase 2, Mudança 3): catálogo de instrumentos General MIDI."""

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
    """Instrumento General MIDI.

    `programa` é o número de program change do MIDI, de 0 a 127
    (é o que o mido usa). Na lista da Wikipédia os instrumentos vão de
    1 a 128, então programa = número_da_lista - 1.
    """

    programa: int
    nome: str


class CatalogoInstrumentos:
    """Conjunto de instrumentos disponíveis no software (mínimo 25).

    Obrigatórios pelo enunciado: Church/Pipe Organ, Tubular Bells, Cravo,
    Órgão, Piano, Fagote, Cordas, Bandoneon, Gaita de Foles, Agogô, e
    Ondas do Mar se continuarem usando.

    ATENÇÃO: o enunciado mistura numerações. "Piano (GM 0)", "Cravo (GM 6)",
    "Fagote (GM 70)" e "Cordas (GM 48)" estão em 0–127; "Church Organ
    (GM 20)", "Tubular Bells (GM 15)", "Bandoneon (#24)" etc. estão em
    1–128. Convertam tudo para 0–127 aqui e documentem a suposição.
    """

    def __init__(self, instrumentos: list[Instrumento]) -> None:
        self._instrumentos: list[Instrumento] = instrumentos
        self._por_programa = {i.programa: i for i in instrumentos}

    @classmethod
    def padrao(cls) -> "CatalogoInstrumentos":
        """Catálogo com os ≥25 instrumentos escolhidos pelo grupo.
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
        """Todos os instrumentos, na ordem de exibição (usado no dropdown)."""
        return list(self._instrumentos)

    def buscar(self, programa: int) -> Instrumento:
        """Raises: KeyError se o programa não estiver no catálogo."""
        return self._por_programa[programa]

    def contem(self, programa: int) -> bool:
        return programa in self._por_programa

    def nome_de(self, programa: int) -> str:
        return self.buscar(programa).nome
