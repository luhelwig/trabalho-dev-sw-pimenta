"""Limites numéricos usados no sistema, reunidos num lugar só.

Evita "números mágicos" espalhados pelo código. Volume e programa MIDI
vão de 0 a 127 pelo padrão MIDI. A oitava vai de 0 a 8 porque, com
altura = 12 * (oitava + 1) + semitom, a oitava 8 é a última completa
dentro de 0–127. O BPM fica entre 20 e 300 (decisão do grupo).
"""

VOLUME_MINIMO = 0
VOLUME_MAXIMO = 127

PROGRAMA_MIDI_MINIMO = 0
PROGRAMA_MIDI_MAXIMO = 127

# Com altura_midi = 12 * (oitava + 1) + semitom, a oitava 8 é a última
# completa dentro de 0–127.
OITAVA_MINIMA = 0
OITAVA_MAXIMA = 8

BPM_MINIMO = 20
BPM_MAXIMO = 300
