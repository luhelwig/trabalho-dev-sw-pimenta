"""Exceções do domínio (erros esperados durante o uso).

Todas herdam de GeradorMusicalErro. A interface captura essa classe base
e mostra a mensagem ao usuário (ex.: "texto vazio", "formato
incorreto"), sem precisar conhecer as regras que geraram o erro.
"""


class GeradorMusicalErro(Exception):
    """Base de todos os erros esperados do sistema."""


class TextoVazioErro(GeradorMusicalErro):
    """Tentativa de gerar música com o campo de texto vazio ou só com espaços."""


class FormatoInvalidoErro(GeradorMusicalErro):
    """O texto tem caracteres fora do alfabeto aceito (ex.: de outros alfabetos)."""


class ArquivoInvalidoErro(GeradorMusicalErro):
    """Arquivo inexistente, que não é .txt, ou "salvar" sem saber onde gravar."""


class MusicaNaoGeradaErro(GeradorMusicalErro):
    """Tentativa de tocar ou exportar antes de gerar a música."""

class AudioIndisponivelErro(GeradorMusicalErro):
    """Este computador não consegue tocar o MIDI.

    Acontece quando o pygame foi instalado sem o módulo de som ou, no Linux,
    quando não há banco de sons (.sf2). O arquivo .mid pode ser salvo mesmo
    assim.
    """
