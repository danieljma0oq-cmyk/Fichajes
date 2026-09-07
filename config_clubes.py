# -*- coding: utf-8 -*-
# Configuración centralizada. Todos estos roles YA EXISTEN en el servidor —
# el bot nunca crea roles, solo los busca por nombre exacto.

# Roles fijos (no ligados a un club en particular)
ROL_DT = "LIGA | Director Tecnico / DT"
ROL_JUGADOR_PRIMERA = "LIGA | Jugador Primera"
ROL_JUGADOR_SEGUNDA = "LIGA | Jugador Segunda"
ROL_AGENTE_LIBRE = "LIGA | Agente Libre"

# 16 clubes de Primera División (1D)
CLUBES_1D = [
    "Real Madrid", "FC Barcelona", "Bayern Munchen", "Manchester City",
    "Liverpool FC", "Paris Saint-Germain", "Juventus", "Inter de Milan",
    "Arsenal FC", "Atletico de Madrid", "Borussia Dortmund", "Bayer Leverkusen",
    "Flamengo", "River Plate", "Boca Juniors", "Palmeiras",
]

# 16 clubes de Segunda División (2D)
CLUBES_2D = [
    "AC Milan", "Chelsea FC", "Manchester United", "SL Benfica",
    "FC Porto", "Ajax", "Sporting CP", "Sevilla FC",
    "AS Roma", "SS Lazio", "Olympique Marseille", "Aston Villa",
    "Tottenham Hotspur", "Independiente", "Club America", "Tigres UANL",
]


def _construir_clubes():
    clubes = []
    for nombre in CLUBES_1D:
        clubes.append({
            "nombre": nombre,
            "division": "Primera",
            "rol_club": f"LIGA | 1D | {nombre}",
            "rol_jugador": ROL_JUGADOR_PRIMERA,
        })
    for nombre in CLUBES_2D:
        clubes.append({
            "nombre": nombre,
            "division": "Segunda",
            "rol_club": f"LIGA | 2D | {nombre}",
            "rol_jugador": ROL_JUGADOR_SEGUNDA,
        })
    return clubes


# Lista final: 32 clubes con su rol de club, división y rol de jugador correspondiente
CLUBES = _construir_clubes()
