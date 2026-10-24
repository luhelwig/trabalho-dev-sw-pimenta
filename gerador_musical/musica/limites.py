"""NOVO: limites numéricos num lugar só (para evitar números mágicos espalhados).

Os valores de MIDI (0–127) são fixos pelo padrão; os demais são
sugestões — o grupo deve confirmar e registrar como suposição.
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
