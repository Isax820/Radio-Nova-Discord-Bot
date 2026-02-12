import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
STREAM_URL = os.getenv("STREAM_URL")
VOLUME = float(os.getenv("VOLUME", "0.6"))
GUILD_ID = os.getenv("GUILD_ID")  # optional: set to speed up slash command registration

intents = discord.Intents.default()
intents.message_content = False
intents.voice_states = True

# Use commands.Bot but register slash commands through bot.tree
bot = commands.Bot(command_prefix="!", intents=intents, description="Radio Nova bot")

FFMPEG_OPTIONS = (
    "-hide_banner -loglevel warning -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
)


def get_voice_channel_from_interaction(interaction: discord.Interaction):
    user = interaction.user
    if not getattr(user, "voice", None) or not user.voice.channel:
        return None
    return user.voice.channel


@bot.event
async def on_ready():
    # Sync commands: guild sync if GUILD_ID provided for fast update, otherwise global
    try:
        if GUILD_ID:
            guild_obj = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild_obj)
            await bot.tree.sync(guild=guild_obj)
            print(f"Slash commands synced to guild {GUILD_ID}")
        else:
            await bot.tree.sync()
            print("Global slash commands synced")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")


@bot.tree.command(name="join")
async def slash_join(interaction: discord.Interaction):
    """Faire rejoindre le bot au canal vocal de l'utilisateur."""
    channel = get_voice_channel_from_interaction(interaction)
    if not channel:
        await interaction.response.send_message("Tu dois être dans un canal vocal.", ephemeral=True)
        return
    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        await vc.move_to(channel)
        await interaction.response.send_message(f"Déplacé dans {channel.mention}.")
        return
    await channel.connect()
    await interaction.response.send_message(f"Connecté à {channel.mention}.")


@bot.tree.command(name="leave")
async def slash_leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected():
        await interaction.response.send_message("Je ne suis pas connecté à un canal vocal.", ephemeral=True)
        return
    await vc.disconnect()
    await interaction.response.send_message("Déconnecté.")


@bot.tree.command(name="playnova")
async def slash_playnova(interaction: discord.Interaction):
    """Jouer le flux STREAM_URL dans le canal vocal."""
    if not STREAM_URL:
        await interaction.response.send_message("Le flux n'est pas configuré. Mets STREAM_URL dans ton .env", ephemeral=True)
        return

    channel = get_voice_channel_from_interaction(interaction)
    if not channel:
        await interaction.response.send_message("Tu dois être dans un canal vocal.", ephemeral=True)
        return

    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected():
        vc = await channel.connect()
    else:
        if vc.channel != channel:
            await vc.move_to(channel)

    if vc.is_playing():
        await interaction.response.send_message("Le flux est déjà en cours de lecture.")
        return

    try:
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(STREAM_URL, before_options=FFMPEG_OPTIONS),
            volume=VOLUME,
        )
        vc.play(source)
        await interaction.response.send_message("Lecture du flux Radio Nova...")
    except Exception as e:
        await interaction.response.send_message(f"Échec de la lecture du flux: {e}")


@bot.tree.command(name="stop")
async def slash_stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected() or not vc.is_playing():
        await interaction.response.send_message("Aucune lecture en cours.", ephemeral=True)
        return
    vc.stop()
    await interaction.response.send_message("Lecture arrêtée.")


@bot.tree.command(name="pause")
async def slash_pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected() or not vc.is_playing():
        await interaction.response.send_message("Rien à mettre en pause.", ephemeral=True)
        return
    vc.pause()
    await interaction.response.send_message("Lecture mise en pause.")


@bot.tree.command(name="resume")
async def slash_resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected() or not vc.is_paused():
        await interaction.response.send_message("Rien à reprendre.", ephemeral=True)
        return
    vc.resume()
    await interaction.response.send_message("Lecture reprise.")


@bot.tree.command(name="volume")
@discord.app_commands.describe(value="Volume entre 0.0 et 2.0")
async def slash_volume(interaction: discord.Interaction, value: float):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected():
        await interaction.response.send_message("Le bot n'est pas connecté.", ephemeral=True)
        return
    if not vc.source:
        await interaction.response.send_message("Aucune source en lecture.", ephemeral=True)
        return
    value = max(0.0, min(2.0, value))
    if isinstance(vc.source, discord.PCMVolumeTransformer):
        vc.source.volume = value
        await interaction.response.send_message(f"Volume réglé à {value}")
    else:
        await interaction.response.send_message("Impossible de régler le volume pour cette source.", ephemeral=True)


@bot.tree.command(name="status")
async def slash_status(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected():
        await interaction.response.send_message("Je ne suis pas connecté.", ephemeral=True)
        return
    playing = vc.is_playing()
    paused = vc.is_paused()
    await interaction.response.send_message(f"Connecté à: {vc.channel.mention} | playing={playing} | paused={paused}")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Erreur: DISCORD_TOKEN non configuré. Copie .env.example -> .env et mets ton token.")
    else:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"Erreur en démarrant le bot: {e}")
