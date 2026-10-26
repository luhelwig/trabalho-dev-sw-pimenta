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

    A primeira regra cujo aceita() for True é aplicada; se nenhuma aceitar,
    aplica-se a regra_padrao (o "senão" da tabela).

    Attributes:
        regras: regras na ordem em que são testadas.
        regra_padrao: regra usada quando nenhuma outra aceita o token.
    """

    def __init__(self, regras: list[RegraMapeamento], regra_padrao: RegraMapeamento) -> None:
        """Cria o mapeamento.

        Args:
            regras: regras na ordem em que devem ser testadas.
            regra_padrao: regra para os tokens que nenhuma outra aceita.
        """
        self.regras: list[RegraMapeamento] = regras
        self.regra_padrao: RegraMapeamento = regra_padrao

    @classmethod
    def padrao(cls) -> "Mapeamento":
        """Monta o mapeamento da Fase 2. É o ÚNICO lugar onde a tabela aparece.

            [n] (início)        RegraAtraso
            A–G (+#/b, :n)      RegraNota
            a–h                 RegraPausa
            espaço              RegraVolume
            ?                   RegraOitava(+1)
            V                   RegraOitava(-1)
            >  /  <             RegraAndamento(+10 / -10)
            !                   RegraInstrumentoFixo(Bandoneon)
            ; e dígitos ímpares RegraInstrumentoFixo(Sinos tubulares)
            ,                   RegraInstrumentoFixo(Agogô)
            dígitos pares       RegraInstrumentoSomaDigito
            todo o resto        RegraRepetirOuPausar (regra padrão)

        Decisões do grupo: '.' não muda mais a oitava (era da Fase 1) e cai na
        regra padrão; as vogais O, I e U também (A e E são notas).

        Returns:
            O Mapeamento pronto.
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
        """Acrescenta uma regra no fim da lista, sem mudar outras classes.

        Exemplo do princípio Aberto/Fechado: estende o mapeamento sem modificar
        o código existente.

        Args:
            regra: regra nova.
        """
        self.regras.append(regra)


    def encontrar_regra(self, token: Token) -> RegraMapeamento:
        """Devolve a primeira regra que aceita o token, ou a regra padrão.

        Args:
            token: token a tratar.
        """
        return next((r for r in self.regras if r.aceita(token)), self.regra_padrao)

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Encontra a regra do token e a aplica.

        Args:
            token: token a tratar.
            contexto: estado da linha.
        """
        self.encontrar_regra(token).aplicar(token, contexto)
