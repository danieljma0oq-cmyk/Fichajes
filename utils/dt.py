import discord
from config_clubes import ROL_DT, CLUBES


def obtener_club_del_dt(miembro: discord.Member):
    """
    Devuelve (club, error). Si hay error, club es None y error es el mensaje a mostrar.
    club es un dict de CLUBES si se encontró exactamente uno.
    """
    guild = miembro.guild

    rol_dt = discord.utils.get(guild.roles, name=ROL_DT)
    if not rol_dt or rol_dt not in miembro.roles:
        return None, "No puedes realizar esta acción porque no eres Director Técnico de ningún club."

    club_encontrado = None
    for club in CLUBES:
        rol_club = discord.utils.get(guild.roles, name=club["rol_club"])
        if rol_club and rol_club in miembro.roles:
            if club_encontrado is not None:
                return None, (
                    "Tenés más de un rol de club asignado, no puedo determinar cuál es tu club. "
                    "Avisá al staff para que revisen tus roles."
                )
            club_encontrado = club

    if not club_encontrado:
        return None, "No tenés ningún club asociado a tu rol de Director Técnico. Avisá al staff."

    return club_encontrado, None
  
