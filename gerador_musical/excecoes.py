"""Exceções do domínio.

A interface captura estas exceções e mostra a mensagem correspondente
(ex.: "texto vazio", "formato incorreto"), sem precisar conhecer as regras.
"""


class GeradorMusicalErro(Exception):
    """Base de todos os erros esperados do sistema."""


class TextoVazioErro(GeradorMusicalErro):
    """Tentativa de gerar música com o campo de entrada vazio."""


class FormatoInvalidoErro(GeradorMusicalErro):
    """Texto contém caracteres fora do alfabeto aceito (ex.: outros alfabetos)."""


class ArquivoInvalidoErro(GeradorMusicalErro):
    """Arquivo inexistente, ilegível ou que não é .txt."""


class MusicaNaoGeradaErro(GeradorMusicalErro):
    """Tentativa de tocar/exportar antes de gerar a música."""
