"""NOVA (Fase 2, Mudança 3): catálogo de instrumentos General MIDI."""

from dataclasses import dataclass


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

    @classmethod
    def padrao(cls) -> "CatalogoInstrumentos":
        """Catálogo com os ≥25 instrumentos escolhidos pelo grupo.

        TODO: requisito ainda marcado como [DEFINIR] na documentação.
        """
        raise NotImplementedError

    def listar(self) -> list[Instrumento]:
        """Todos os instrumentos, na ordem de exibição (usado no dropdown)."""
        raise NotImplementedError

    def buscar(self, programa: int) -> Instrumento:
        """Raises: KeyError se o programa não estiver no catálogo."""
        raise NotImplementedError

    def contem(self, programa: int) -> bool:
        raise NotImplementedError

    def nome_de(self, programa: int) -> str:
        raise NotImplementedError
