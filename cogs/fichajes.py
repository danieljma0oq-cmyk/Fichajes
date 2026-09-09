import discord
from discord.ext import commands

import database as db
from config_clubes import CLUBES, ROL_JUGADOR_PRIMERA, ROL_JUGADOR_SEGUNDA, ROL_AGENTE_LIBRE
from utils.embeds import embed_error, embed_exito
from utils.dt import obtener_club_del_dt
from utils.canales import solo_canal_fichajes


class FichajeView(discord.ui.View):
    """Vista persistente: sigue funcionando aunque el bot se reinicie, mientras el fichaje siga PENDING."""

    def __init__(self, fichaje_id: int):
        super().__init__(timeout=None)
        self.fichaje_id = fichaje_id

        boton_aceptar = discord.ui.Button(
            label="Aceptar fichaje", style=discord.ButtonStyle.success, emoji="🟢",
            custom_id=f"fichaje_aceptar_{fichaje_id}"
        )
        boton_aceptar.callback = self.aceptar
        self.add_item(boton_aceptar)

        boton_rechazar = discord.ui.Button(
            label="Rechazar fichaje", style=discord.ButtonStyle.danger, emoji="🔴",
            custom_id=f"fichaje_rechazar_{fichaje_id}"
        )
        boton_rechazar.callback = self.rechazar
        self.add_item(boton_rechazar)

    async def _validar_interaccion(self, interaction: discord.Interaction):
        """Devuelve el fichaje si la interacción es válida, o None (ya respondió con el error)."""
        fichaje = db.obtener_fichaje(self.fichaje_id)

        if interaction.user.id != fichaje["jugador_id"]:
            await interaction.response.send_message(
                f"❌ No puedes responder a este fichaje.\n\n"
                f"Esta solicitud está dirigida únicamente a <@{fichaje['jugador_id']}>.",
                ephemeral=True
            )
            return None

        if fichaje["estado"] != "PENDING":
            await interaction.response.send_message(
                "❌ Esta solicitud ya no está pendiente (ya fue aceptada, rechazada o cancelada).",
                ephemeral=True
            )
            return None

        return fichaje

    async def aceptar(self, interaction: discord.Interaction):
        fichaje = await self._validar_interaccion(interaction)
        if not fichaje:
            return

        guild = interaction.guild
        jugador = guild.get_member(fichaje["jugador_id"])

        rol_club = discord.utils.get(guild.roles, name=fichaje["club_rol_nombre"])
        rol_jugador_nuevo = discord.utils.get(guild.roles, name=fichaje["jugador_rol_nombre"])
        rol_agente_libre = discord.utils.get(guild.roles, name=ROL_AGENTE_LIBRE)
        rol_opuesto_nombre = ROL_JUGADOR_SEGUNDA if fichaje["division"] == "Primera" else ROL_JUGADOR_PRIMERA
        rol_jugador_opuesto = discord.utils.get(guild.roles, name=rol_opuesto_nombre)

        a_quitar = [r for r in [rol_agente_libre, rol_jugador_opuesto] if r and r in jugador.roles]

        # Quitar cualquier rol de club anterior (si el jugador venía de otro club)
        for club in CLUBES:
            if club["rol_club"] == fichaje["club_rol_nombre"]:
                continue
            rol_anterior = discord.utils.get(guild.roles, name=club["rol_club"])
            if rol_anterior and rol_anterior in jugador.roles:
                a_quitar.append(rol_anterior)

        a_agregar = [r for r in [rol_club, rol_jugador_nuevo] if r]

        try:
            if a_quitar:
                await jugador.remove_roles(*a_quitar, reason=f"Fichaje #{self.fichaje_id} aceptado")
            if a_agregar:
                await jugador.add_roles(*a_agregar, reason=f"Fichaje #{self.fichaje_id} aceptado")
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para modificar los roles de este usuario. "
                "Revisá que mi rol esté por encima de los roles de club y de Agente Libre.",
                ephemeral=True
            )
            return

        db.actualizar_estado(self.fichaje_id, "COMPLETED")
        db.cancelar_otras_pendientes(fichaje["jugador_id"], excepto_id=self.fichaje_id)

        embed = discord.Embed(title="✅ FICHAJE COMPLETADO", color=discord.Color.green())
        embed.description = (
            f"<@{fichaje['jugador_id']}> ha aceptado el fichaje.\n\n"
            f"🏟️ Nuevo club: **{fichaje['club_nombre']}**\n"
            f"🏆 División: **{fichaje['division']} División**\n\n"
            f"Se han actualizado correctamente sus roles."
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    async def rechazar(self, interaction: discord.Interaction):
        fichaje = await self._validar_interaccion(interaction)
        if not fichaje:
            return

        db.actualizar_estado(self.fichaje_id, "REJECTED")

        embed = discord.Embed(title="❌ FICHAJE RECHAZADO", color=discord.Color.red())
        embed.description = (
            f"<@{fichaje['jugador_id']}> ha rechazado la propuesta de fichaje por **{fichaje['club_nombre']}**.\n\n"
            f"👔 <@{fichaje['dt_id']}>, podés volver a intentarlo con `!fichar` si el rechazo fue un error."
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


class FichajesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fichar")
    @solo_canal_fichajes()
    async def fichar(self, ctx, jugador: discord.Member):
        """Un DT solicita fichar a un jugador para su propio club. Uso: !fichar @usuario"""
        club, error = obtener_club_del_dt(ctx.author)
        if error:
            await ctx.send(embed=embed_error(error))
            return

        rol_club_actual = discord.utils.get(ctx.guild.roles, name=club["rol_club"])
        if rol_club_actual and rol_club_actual in jugador.roles:
            await ctx.send(embed=embed_error(f"{jugador.mention} ya pertenece a **{club['nombre']}**."))
            return

        fichaje_id = db.crear_fichaje(ctx.guild.id, ctx.author.id, jugador.id, club)

        embed = discord.Embed(title="⚽ SOLICITUD DE FICHAJE", color=discord.Color.blue())
        embed.add_field(name="👤 Jugador", value=jugador.mention, inline=True)
        embed.add_field(name="🏟️ Club", value=club["nombre"], inline=True)
        embed.add_field(name="🏆 División", value=f"{club['division']} División", inline=True)
        embed.add_field(name="👔 Solicitado por", value=ctx.author.mention, inline=False)
        embed.set_footer(text="¿Aceptas el fichaje?")

        await ctx.send(embed=embed, view=FichajeView(fichaje_id))

    @fichar.error
    async def fichar_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass  # el mensaje ya lo mandó el check de canal
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=embed_error("No encontré a ese usuario. Mencionalo con @."))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=embed_error("Uso correcto: `!fichar @usuario`"))
        else:
            await ctx.send(embed=embed_error(f"Ocurrió un error: {error}"))
            print(f"Error en !fichar: {error}")


async def setup(bot):
    await bot.add_cog(FichajesCog(bot))
