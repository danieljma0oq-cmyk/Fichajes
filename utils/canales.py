from discord.ext import commands

CANAL_FICHAJES = 1546405363748700222
CANAL_BAJAS = 1546405364562399233


def _solo_canal(canal_id, nombre_canal):
    async def predicate(ctx):
        if ctx.channel.id == canal_id:
            return True
        await ctx.send(f"❌ Este comando solo se puede usar en <#{canal_id}>.")
        return False

    return commands.check(predicate)


def solo_canal_fichajes():
    """Decorador: !fichar solo puede usarse en el canal de fichajes."""
    return _solo_canal(CANAL_FICHAJES, "fichajes")


def solo_canal_bajas():
    """Decorador: !baja solo puede usarse en el canal de bajas."""
    return _solo_canal(CANAL_BAJAS, "bajas")
  
