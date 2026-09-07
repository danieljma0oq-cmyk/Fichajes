import discord
from discord.ext import commands

from config_clubes import ROL_AGENTE_LIBRE
from utils.embeds import embed_error, embed_exito
from utils.dt import obtener_club_del_dt


class BajasCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="baja")
    async def baja(self, ctx, jugador: discord.Member):
        """Un DT da de baja a un jugador de su propio club. Uso: !baja @usuario"""
        club, error = obtener_club_del_dt(ctx.author)
        if error:
            await ctx.send(embed=embed_error(error))
            return

        rol_club = discord.utils.get(ctx.guild.roles, name=club["rol_club"])
        if not rol_club or rol_club not in jugador.roles:
            await ctx.send(embed=embed_error(
                f"No puedes dar de baja a este jugador.\n\nEl jugador no pertenece a tu club (**{club['nombre']}**)."
            ))
            return

        rol_jugador = discord.utils.get(ctx.guild.roles, name=club["rol_jugador"])
        rol_agente_libre = discord.utils.get(ctx.guild.roles, name=ROL_AGENTE_LIBRE)

        a_quitar = [r for r in [rol_club, rol_jugador] if r and r in jugador.roles]
        a_agregar = [rol_agente_libre] if rol_agente_libre else []

        try:
            if a_quitar:
                await jugador.remove_roles(*a_quitar, reason=f"Baja de {club['nombre']} por {ctx.author}")
            if a_agregar:
                await jugador.add_roles(*a_agregar, reason=f"Baja de {club['nombre']} por {ctx.author}")
        except discord.Forbidden:
            await ctx.send(embed=embed_error(
                "No tengo permisos suficientes para modificar los roles de este usuario."
            ))
            return

        embed = discord.Embed(title="📤 BAJA REALIZADA", color=discord.Color.orange())
        embed.description = (
            f"{jugador.mention} fue dado de baja de **{club['nombre']}**.\n\n"
            f"Ahora queda registrado como **Agente Libre**."
        )
        await ctx.send(embed=embed)

    @baja.error
    async def baja_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=embed_error("No encontré a ese usuario. Mencionalo con @."))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=embed_error("Uso correcto: `!baja @usuario`"))
        else:
            await ctx.send(embed=embed_error(f"Ocurrió un error: {error}"))
            print(f"Error en !baja: {error}")


async def setup(bot):
    await bot.add_cog(BajasCog(bot))
  
