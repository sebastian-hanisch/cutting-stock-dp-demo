"""Defaults, slider bounds und Presets für die Cutting-Stock-DP-Demo."""

DEFAULT_N_TYPES = 4
DEFAULT_MAX_DEMAND = 2
DEFAULT_ROLL_WIDTH = 100
DEFAULT_SEED = 7

N_TYPES_MIN, N_TYPES_MAX = 2, 8
MAX_DEMAND_MIN, MAX_DEMAND_MAX = 1, 5
ROLL_WIDTH_MIN, ROLL_WIDTH_MAX = 50, 200

WIDTH_FRACTION_RANGE = (0.15, 0.6)

# DP liefert kein Zwischenergebnis, solange nicht alle nötigen Zustände berechnet
# sind (anders als Suchbaum-Verfahren) - bei Überschreiten wird gar nicht erst
# gerechnet. Kalibriert per Prototyp: n=8/demand=4 erreicht ~24.000 Zustände in
# 2.2s (soll noch durchlaufen), n=8/demand=5 ~65.000 Zustände in 6.9s (soll die
# Grenze auslösen).
MAX_STATES_EXPLORED = 40_000

PRESETS = {
    "Winzige Instanz (Zustandsraum komplett sichtbar)": {
        "n_types": 3, "roll_width": 100, "max_demand": 2, "seed": 1,
    },
    "Wachsender Zustandsraum (noch schnell)": {
        "n_types": 6, "roll_width": 100, "max_demand": 4, "seed": 2,
    },
    "Grenze erreicht (Column Generation wird nötig)": {
        "n_types": 8, "roll_width": 100, "max_demand": 5, "seed": 2,
    },
}
