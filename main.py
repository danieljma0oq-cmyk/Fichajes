import os
import asyncio
import discord
from discord.ext import commands

import database as db
from cogs.fichajes import FichajeView

PREFIJO = "!"
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIJO, intents=intents, help_command=None)

COGS = [
    "cogs.fichajes",
    "cogs.bajas",
]


@bot.event
async def on_ready():
    # Vuelve a activar los botones de cualquier fichaje que haya quedado pendiente
    # antes de que el bot se reiniciara (por ejemplo, un redeploy en Railway).
    pendientes = db.obtener_pendientes()
    for fila in pendientes:
        bot.add_view(FichajeView(fila["id"]))

    print(f"✅ Bot conectado como {bot.user}")
    print(f"Fichajes pendientes reactivados: {len(pendientes)}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.CheckFailure):
        pass
    else:
        await ctx.send(f"❌ Ocurrió un error: `{error}`")
        print(f"Error: {error}")


@bot.command(name="ayuda")
async def ayuda(ctx):
    embed = discord.Embed(title="📖 Comandos disponibles", color=discord.Color.blue())
    embed.add_field(
        name="Para Directores Técnicos",
        value=(
            "`!fichar @usuario` — solicitar el fichaje de un jugador para tu club\n"
            "`!baja @usuario` — dar de baja a un jugador de tu club"
        ),
        inline=False
    )
    await ctx.send(embed=embed)


async def main():
    db.inicializar()
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
  
