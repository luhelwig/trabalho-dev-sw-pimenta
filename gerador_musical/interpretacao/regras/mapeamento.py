"""NOVA (Fase 2): tabela de mapeamento = lista ordenada de regras."""

from gerador_musical.interpretacao.regras.regras_eventos import RegraNota, RegraPausa, RegraRepetirOuPausar
from gerador_musical.interpretacao.regras.regras_globais import RegraAndamento
from gerador_musical.interpretacao.regras.regras_voz import (
    RegraAtraso, RegraInstrumentoFixo, RegraInstrumentoSomaDigito, RegraOitava, RegraVolume,
)
from gerador_musical.musica.instrumentos import AGOGO, BANDONEON, TUBULAR_BELLS
from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.regras.regra_mapeamento import RegraMapeamento
from gerador_musical.interpretacao.tokens import Token

class Mapeamento:
    """Escolhe qual regra aplicar a cada token.

    A primeira regra cujo aceita() for True é aplicada; se nenhuma
    aceitar, aplica-se a regra_padrao (o "ELSE" da tabela).
    """

    def __init__(self, regras: list[RegraMapeamento], regra_padrao: RegraMapeamento) -> None:
        self.regras: list[RegraMapeamento] = regras
        self.regra_padrao: RegraMapeamento = regra_padrao

    @classmethod
    def padrao(cls) -> "Mapeamento":
        """Monta o mapeamento da Fase 2. ÚNICO lugar onde a tabela aparece:

            [n] (início)      RegraAtraso
            A–G (+#/b, :n)    RegraNota
            a–h               RegraPausa
            espaço            RegraVolume                    (ver ressalva)
            ?                 RegraOitava(+1)
            V                 RegraOitava(-1)
            >  /  <           RegraAndamento(+10 / -10)
            !                 RegraInstrumentoFixo(Bandoneon)
            ; e ímpares       RegraInstrumentoFixo(Tubular Bells)
            ,                 RegraInstrumentoFixo(Agogô)
            pares             RegraInstrumentoSomaDigito
            resto (H, O, I,
              U, consoantes)  RegraRepetirOuPausar  (regra_padrao)

        TODO (decisão do grupo): '.' ainda sobe oitava (Fase 1)? Vogais
        continuam trocando para Gaita de Foles (Fase 1) ou seguem o
        "repete/pausa" (texto da Fase 2)?
        """
        return cls(
            regras=[
                RegraAtraso(),
                RegraNota(),
                RegraPausa(),
                RegraVolume(),
                RegraOitava("?", +1),
                RegraOitava("V", -1),
                RegraAndamento(">", +10),
                RegraAndamento("<", -10),
                RegraInstrumentoFixo("!", BANDONEON),
                RegraInstrumentoFixo(";13579", TUBULAR_BELLS),
                RegraInstrumentoFixo(",", AGOGO),
                RegraInstrumentoSomaDigito(),
            ],
            regra_padrao=RegraRepetirOuPausar(),
        )

    def adicionar_regra(self, regra: RegraMapeamento) -> None:
        """Extensão sem modificar código existente (Aberto/Fechado)."""
        self.regras.append(regra)


    def encontrar_regra(self, token: Token) -> RegraMapeamento:
        return next((r for r in self.regras if r.aceita(token)), self.regra_padrao)

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        self.encontrar_regra(token).aplicar(token, contexto)
