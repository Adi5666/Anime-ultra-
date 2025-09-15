
from keep_alive import keep_alive
keep_alive()
import os, asyncio, discord
from discord.ext import commands
from src/core.db import init_db
from src.core.logger import log
from src.services.prefixes import get_prefix

TOKEN = os.environ.get("DISCORD_TOKEN")

async def dynamic_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or("!")(bot, message)
    prefix = await get_prefix(str(message.guild.id))
    return commands.when_mentioned_or(prefix)(bot, message)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=dynamic_prefix, intents=intents)

COGS = [
  "help","error_handler","utility","roles",
  "premium","premium_owner",
  "hint","guess","incense","spawn_listener",
  "gameplay","packs","trading","capital"
]

async def load_cogs():
    for c in COGS:
        try:
            await bot.load_extension(f"src.cogs.{c}")
            log.info(f"Loaded cog: {c}")
        except Exception as e:
            log.error(f"Failed to load cog {c}: {e}")

@bot.event
async def on_ready():
    log.info(f"Anime Ultra online as {bot.user}")
    await init_db()
    await bot.tree.sync()
    log.info("Slash commands synced.")

async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
