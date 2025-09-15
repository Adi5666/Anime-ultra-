import pathlib, json

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Catalog seed ---
write("src/content/catalog.json", json.dumps({
  "version": "1.0",
  "families": {
    "starter": [
      {
        "name": "Starter Hero",
        "safe_image": "https://images.unsplash.com/photo-1608889175136-85f7cc0b5f3a?q=80&w=1200&auto=format",
        "authentic_image": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?q=80&w=1200&auto=format",
        "rarity": "UNCOMMON",
        "base": {"atk": 12, "def": 11, "spd": 12},
        "ability": "Signature Technique",
        "shiny_ability": "Ultra Instinct",
        "lore": "A mysterious hero whose legend is about to begin."
      }
    ]
  }
}, indent=2))

# --- App loader (Render-ready) ---
write("src/app.py", r'''\
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
''')

print("bootstrap_all Part 8 applied: catalog.json and app.py written.")

