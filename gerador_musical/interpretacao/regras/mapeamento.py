"""NOVA (Fase 2): tabela de mapeamento = lista ordenada de regras."""

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.regras.regra_mapeamento import RegraMapeamento
from gerador_musical.interpretacao.tokens import Token
from gerador_musical.musica.instrumentos import CatalogoInstrumentos


class Mapeamento:
    """Escolhe qual regra aplicar a cada token.

    A primeira regra cujo aceita() for True é aplicada; se nenhuma
    aceitar, aplica-se a regra_padrao (o "ELSE" da tabela).
    """

    def __init__(self, regras: list[RegraMapeamento], regra_padrao: RegraMapeamento) -> None:
        self.regras: list[RegraMapeamento] = regras
        self.regra_padrao: RegraMapeamento = regra_padrao

    @classmethod
    def padrao(cls, catalogo: CatalogoInstrumentos) -> "Mapeamento":
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
        raise NotImplementedError

    def adicionar_regra(self, regra: RegraMapeamento) -> None:
        """Extensão sem modificar código existente (Aberto/Fechado)."""
        raise NotImplementedError

    def encontrar_regra(self, token: Token) -> RegraMapeamento:
        raise NotImplementedError

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError
