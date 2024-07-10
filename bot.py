import discord
from discord.ext import commands
from datetime import datetime
import config
import language

# Token aus der Konfigurationsdatei laden
TOKEN = config.TOKEN
LOG_CHANNEL_ID = config.LOG_CHANNEL_ID
LANGUAGE = config.LANGUAGE

# Erstellen von Intents, um bestimmte Ereignisse zu abonnieren
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

# Initialisieren des Bots mit einem benutzerdefinierten Befehlspräfix und den definierten Intents
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Ereignis, das ausgeführt wird, wenn der Bot erfolgreich eingeloggt ist
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')
    print(f'Bot ID: {bot.user.id}')
    print(f'Connected to {len(bot.guilds)} guild(s):')
    for guild in bot.guilds:
        print(f' - {guild.name} (ID: {guild.id})')
    print(f'Invite link: https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8')

# Cog für allgemeine Befehle definieren
class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_language = config.LANGUAGE

    # Status-Befehl, nur für Administratoren
    @commands.command(name='status')
    @commands.has_permissions(administrator=True)
    async def status(self, ctx):
        message = language.get_translation(self.default_language, "status").format(guilds=len(self.bot.guilds))
        await ctx.send(message)

    # Befehlsliste anzeigen
    @commands.command(name='commands')
    async def commands_list(self, ctx):
        message = language.get_translation(self.default_language, "commands")
        await ctx.send(message)

    # Einladungslink anzeigen
    @commands.command(name='invite')
    async def invite(self, ctx):
        message = language.get_translation(self.default_language, "invite").format(link=config.INVITE_LINK)
        await ctx.send(message)

    # Aktuelle Uhrzeit anzeigen
    @commands.command(name='time')
    async def time(self, ctx):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = language.get_translation(self.default_language, "time").format(time=current_time)
        await ctx.send(message)

    # Serverinformationen anzeigen
    @commands.command(name='serverinfo')
    async def serverinfo(self, ctx):
        server_info = (f'{language.get_translation(self.default_language, "server_name")}: {ctx.guild.name}\n'
                       f'{language.get_translation(self.default_language, "total_members")}: {ctx.guild.member_count}\n'
                       f'{language.get_translation(self.default_language, "server_created_at")}: {ctx.guild.created_at}')
        await ctx.send(server_info)

    # Benutzerinformationen anzeigen
    @commands.command(name='userinfo')
    async def userinfo(self, ctx):
        if len(ctx.message.mentions) > 0:
            user = ctx.message.mentions[0]
            user_info = (f'{language.get_translation(self.default_language, "user_name")}: {user.name}\n'
                         f'{language.get_translation(self.default_language, "discriminator")}: {user.discriminator}\n'
                         f'{language.get_translation(self.default_language, "id")}: {user.id}\n'
                         f'{language.get_translation(self.default_language, "status")}: {user.status}\n'
                         f'{language.get_translation(self.default_language, "joined_at")}: {user.joined_at}\n'
                         f'{language.get_translation(self.default_language, "account_created_at")}: {user.created_at}')
            await ctx.send(user_info)
        else:
            await ctx.send(language.get_translation(self.default_language, "mention_user"))

    # Bot-Latenzzeit anzeigen
    @commands.command(name='ping')
    async def ping(self, ctx):
        latency = self.bot.latency
        message = language.get_translation(self.default_language, "ping").format(latency=latency * 1000)
        await ctx.send(message)

    # Hilfe-Befehl
    @commands.command(name='help')
    async def help_command(self, ctx):
        message = language.get_translation(self.default_language, "help")
        await ctx.send(message)

# Funktion zum Hinzufügen des General-Cogs
async def setup_general():
    if bot.get_cog('General') is None:
        await bot.add_cog(General(bot))

# Cog für das Protokollieren von Nachrichten definieren
class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_language = config.LANGUAGE

    # Funktion zum Protokollieren von Nachrichten
    async def log_message(self, message):
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel is not None:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            guild_name = message.guild.name if message.guild else 'Direct Message'
            log_message_content = f'[{guild_name} | {current_time}] {message.author.name.replace("@", "°")}: {message.content}'
            try:
                await log_channel.send(log_message_content)
                print(f'Message logged in {log_channel.name} successfully.')
            except discord.HTTPException as e:
                print(f'Failed to log message in channel: {log_channel.name}. Error: {e}')

    # Ereignis-Listener für neue Nachrichten
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return  # Nachrichten des Bots ignorieren
        await self.log_message(message)

    # Ereignis-Listener für Befehlsfehler
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(language.get_translation(self.default_language, "missing_permissions"))
        else:
            await ctx.send(language.get_translation(self.default_language, "error"))
            print(f'Error: {error}')

# Funktion zum Hinzufügen des Logging-Cogs
async def setup_logging():
    if bot.get_cog('Logging') is None:
        await bot.add_cog(Logging(bot))

# Cog für Ereignisse definieren
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_language = config.LANGUAGE

    # Ereignis-Listener für Voice-Channel-Updates
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel is not None:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            guild_name = member.guild.name if member.guild else 'Unknown Server'
            if before.channel != after.channel:
                if before.channel:
                    log_message = f'{member.display_name} {language.get_translation(self.default_language, "left_voice_channel")} "{before.channel.name}"'
                if after.channel:
                    log_message = f'{member.display_name} {language.get_translation(self.default_language, "joined_voice_channel")} "{after.channel.name}"'
                try:
                    await log_channel.send(f'[{guild_name} | {current_time}] {log_message}')
                    print(f'Voice channel update logged in {log_channel.name} successfully.')
                except discord.HTTPException as e:
                    print(f'Failed to log voice channel update in channel: {log_channel.name}. Error: {e}')

    # Ereignis-Listener für Befehlsfehler
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(language.get_translation(self.default_language, "missing_permissions"))
        else:
            await ctx.send(language.get_translation(self.default_language, "error"))
            print(f'Error: {error}')

# Funktion zum Hinzufügen des Events-Cogs
async def setup_events():
    if bot.get_cog('Events') is None:
        await bot.add_cog(Events(bot))

# Hauptfunktion zum Starten des Bots und Hinzufügen der Cogs
async def main():
    await setup_general()
    await setup_logging()
    await setup_events()
    await bot.start(TOKEN)

# Ausführen der Hauptfunktion
import asyncio
asyncio.run(main())
